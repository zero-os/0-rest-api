package backup

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	tools "github.com/zero-os/0-orchestrator/api/tools"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// BackupAPI is API implementation of /backup root endpoint
type BackupAPI struct {
	AysRepo     string
	AysUrl      string
	AysRetries  string
	JWTProvider *tools.JWTProvider
}

func NewBackupAPI(repo string, aysUrl string, aysRetries string, jwtProvider *tools.JWTProvider) *BackupAPI {
	return &BackupAPI{
		AysRepo:     repo,
		AysUrl:      aysUrl,
		AysRetries:  aysRetries,
		JWTProvider: jwtProvider,
	}
}

func (api *BackupAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api *BackupAPI) AysRepoName() string {
	return api.AysRepo
}

func (api *BackupAPI) GetJWT() (string, error) {
	return api.JWTProvider.GetJWT()
}

func (api *BackupAPI) AysRetriesConfig() string {
	return api.AysRetries
}
