package main

import "reflect"

var typeRegistry = map[string]reflect.Type{}

func Register(name string, sample any) error {
	panic("not implemented: Register")
}

func Create(typeName string) (any, error) {
	panic("not implemented: Create")
}
