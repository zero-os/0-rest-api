package ays

import (
	"crypto/ecdsa"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
	"time"

	log "github.com/Sirupsen/logrus"
	jwt "github.com/dgrijalva/jwt-go"
	cache "github.com/robfig/go-cache"
	client "github.com/zero-os/0-orchestrator/api/ays/ays-client"
	"github.com/zero-os/0-orchestrator/api/ays/callback"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// Client is the main type of this package, it prove an easy to use API on top of the
// AYS client generated by-goraml
type Client struct {
	// the name of the repos
	repo   string
	client *client.AtYourServiceAPI

	// used to manage direct connection to the nodes and containers
	connectionMgr *connectionMgr
	// cache for container ids
	cache *cache.Cache

	iyoOrganization string
	iyoAppID        string
	iyoSecret       string
	token           string

	cbMgr *callback.Mgr
}

// NewClient create a new AYS client for a specific AYS repository
// if token is not empty, the Authorization header will be fill with the token and send for each request
func NewClient(url, repo, org, appID, secret string) (*Client, error) {
	cl := &Client{
		repo:            repo,
		iyoOrganization: org,
		iyoAppID:        appID,
		iyoSecret:       secret,

		cache: cache.New(5*time.Minute, 1*time.Minute),

		client: client.NewAtYourServiceAPI(),
		cbMgr:  callback.NewMgr(fmt.Sprintf("%s/callback", url)),
	}
	cl.connectionMgr = newConnectionMgr(cl)

	// TODO: auto refresh
	token, err := getToken("", appID, secret, org)
	if err != nil {
		return nil, err
	}

	cl.client.AuthHeader = fmt.Sprintf("Bearer %s", token)
	cl.client.BaseURI = url

	return cl, nil
}

func (c *Client) AYS() *client.AysService {
	// TODO: refresh token
	return c.client.Ays
}

func (c *Client) CallbackHandler() http.HandlerFunc {
	return c.cbMgr.Handler
}

// CreateExecRun creates and executes a blueprint, and then schedules a run for it.
// If wait == true then this method will also wait until the run and all its reties have finished
// or timeout after 1h
func (c *Client) CreateExecRun(name string, bp Blueprint, wait bool) (*Run, error) {
	if err := c.CreateBlueprint(name, bp); err != nil {
		return nil, err
	}

	if _, err := c.ExecuteBlueprint(name); err != nil {
		return nil, err
	}

	return c.CreateRun(false, wait)
}

// CreateExec creates and executes a blueprint, and waits until the jobs created by AYS have executed
func (c *Client) CreateExec(blueprintName string, blueprint Blueprint) error {
	if err := c.CreateBlueprint(blueprintName, blueprint); err != nil {
		return err
	}

	processJobs, err := c.ExecuteBlueprint(blueprintName)
	if err != nil {
		return err
	}

	return processJobs.Wait()
}

// HandleError examines the err error object and will return a correct error notification to the http response
func (c *Client) HandleError(w http.ResponseWriter, err error) {
	if ayserr, ok := err.(*Error); ok {
		ayserr.Handle(w, http.StatusInternalServerError)
	} else {
		httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
	}
	return
}

func getToken(token string, applicationID string, secret string, org string) (string, error) {
	if token == "" {
		token, err := refreshToken(applicationID, secret, org)
		if err != nil {
			return "", err
		}
		return token, nil
	}

	claim, err := getJWTClaim(token)
	if err != nil {
		return "", err
	}
	exp := claim["exp"].(float64)
	if exp < 300 {
		token, err = refreshToken(applicationID, secret, org)
		if err != nil {
			return "", err
		}
	}
	return token, nil
}

func refreshToken(applicationID string, secret string, org string) (string, error) {
	url := fmt.Sprintf("https://itsyou.online/v1/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials&response_type=id_token&scope=user:memberof:%s,offline_access", applicationID, secret, org)
	resp, err := http.Post(url, "", nil)
	if err != nil {
		return "", err
	}

	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("invalid appliaction-id and secret")
	}

	bodyBytes, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	token := string(bodyBytes)
	return token, nil
}

func getJWTClaim(tokenStr string) (jwt.MapClaims, error) {
	jwtStr := strings.TrimSpace(strings.TrimPrefix(tokenStr, "Bearer"))
	token, err := jwt.Parse(jwtStr, func(token *jwt.Token) (interface{}, error) {
		if token.Method != jwt.SigningMethodES384 {
			return nil, fmt.Errorf("Unexpected signing method: %v", token.Header["alg"])
		}
		return JWTPublicKey, nil
	})

	if err != nil {
		return nil, err
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return nil, fmt.Errorf("Invalid claims")
	}

	return claims, nil
}

var JWTPublicKey *ecdsa.PublicKey

const (
	oauth2ServerPublicKey = `\
-----BEGIN PUBLIC KEY-----
MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n2
7MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny6
6+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv
-----END PUBLIC KEY-----`

	maxJWTDuration int64 = 3600 //1 hour
)

func init() {
	var err error

	if len(oauth2ServerPublicKey) == 0 {
		return
	}

	JWTPublicKey, err = jwt.ParseECPublicKeyFromPEM([]byte(oauth2ServerPublicKey))
	if err != nil {
		log.Fatalf("failed to parse pub key:%v", err)
	}
}
