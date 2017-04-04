package client

import (
	"encoding/json"

	"gopkg.in/validator.v2"
)

type Blueprint struct {
	Archived bool            `json:"archived" validate:"nonzero"`
	Content  json.RawMessage `json:"content" validate:"nonzero"`
	Hash     string          `json:"hash" validate:"nonzero"`
	Name     string          `json:"name" validate:"nonzero"`
	Path     string          `json:"path" validate:"nonzero"`
}

func (s Blueprint) Validate() error {

	return validator.Validate(s)
}
