package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	runs "github.com/zero-os/0-orchestrator/api/run"
	"github.com/zero-os/0-orchestrator/api/tools"
)

type CreateGWBP struct {
	Node         string        `json:"node" yaml:"node"`
	Domain       string        `json:"domain" yaml:"domain"`
	Nics         []GWNIC       `json:"nics" yaml:"nics"`
	Httpproxies  []HTTPProxy   `json:"httpproxies" yaml:"httpproxies"`
	Portforwards []PortForward `json:"portforwards" yaml:"portforwards"`
	Advanced     bool          `json:"advanced" yaml:"advanced"`
}

// CreateGW is the handler for POST /nodes/{nodeid}/gws
// Create a new gateway
func (api NodeAPI) CreateGW(w http.ResponseWriter, r *http.Request) {
	var reqBody GWCreate

	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

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

	exists, err := tools.ServiceExists("gateway", reqBody.Name, api.AysRepo)
	if err != nil {
		errmsg := fmt.Sprintf("error getting gateway service by name %s ", reqBody.Name)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	if exists {
		tools.WriteError(w, http.StatusConflict, fmt.Errorf("A gateway with name %s already exists", reqBody.Name), "")
		return
	}

	gateway := CreateGWBP{
		Node:         nodeID,
		Domain:       reqBody.Domain,
		Nics:         reqBody.Nics,
		Httpproxies:  reqBody.Httpproxies,
		Portforwards: reqBody.Portforwards,
		Advanced:     false,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", reqBody.Name)] = gateway
	obj["actions"] = []tools.ActionBlock{{Action: "install", Service: reqBody.Name, Actor: "gateway"}}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", reqBody.Name, "install", obj)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for gateway %s creation ", reqBody.Name)
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	response := runs.Run{Runid: run.Key, State: runs.EnumRunState(run.State)}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s", nodeID, reqBody.Name))
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(&response)

}
