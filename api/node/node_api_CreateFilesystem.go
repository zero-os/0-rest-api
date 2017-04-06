package node

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// CreateFilesystem is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem
// Create a new filesystem
func (api NodeAPI) CreateFilesystem(w http.ResponseWriter, r *http.Request) {
	var reqBody FilesystemCreate
	nodeid := mux.Vars(r)["nodeid"]
	storagepool := mux.Vars(r)["storagepoolname"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	bpContent := struct {
		FilesystemCreate
		StoragePool string `json:"storagePool"`
	}{
		FilesystemCreate: reqBody,
		StoragePool:      storagepool,
	}

	blueprint := map[string]interface{}{
		fmt.Sprintf("filesystem__%s", reqBody.Name): bpContent,
		"actions": []map[string]string{{"action": "install"}},
	}

	blueprintName := fmt.Sprintf("filesystem__%s_create_%d", storagepool, time.Now().Unix())

	if _, err := tools.ExecuteBlueprint(api.AysRepo, blueprintName, blueprint); err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for filesystem creation : %+v", err.Error())
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
	}

	w.Header().Set("Location", fmt.Sprintf("/node/%s/storagepool/%s/filesystem/%s", nodeid, storagepool, reqBody.Name))
	w.WriteHeader(http.StatusCreated)
}
