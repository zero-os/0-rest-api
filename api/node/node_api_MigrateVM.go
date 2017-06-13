package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// MigrateVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/migrate
// Migrate the VM to another host
func (api NodeAPI) MigrateVM(w http.ResponseWriter, r *http.Request) {
	var reqBody VMMigrate

	vmID := mux.Vars(r)["vmid"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// Create migrate blueprint
	bp := struct {
		Node string `yaml:"node" json:"node"`
	}{
		Node: reqBody.Nodeid,
	}

	decl := fmt.Sprintf("vm__%v", vmID)

	obj := make(map[string]interface{})
	obj[decl] = bp
	obj["actions"] = []tools.ActionBlock{{
		Action:  "migrate",
		Actor:   "vm",
		Service: vmID,
		Force:   true,
	}}

	// And execute
	api.AysAPI.AuthHeader = r.Header.Get("Authorization")
	if _, err := tools.ExecuteBlueprint(api.AysRepo, "vm", vmID, "migrate", obj); err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for vm %s migrate ", vmID)
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
