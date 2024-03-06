package cython

/*
#cgo pkg-config: python3
#cgo LDFLAGS: -lpython3.12
#include <Python.h>
*/
import "C"

import (
	"errors"
	"log"
	"unsafe"
)

var ErrInvalidFuncEval = errors.New("something goes wrong. Pass correct func args")

type Func struct {
	ptr *C.struct__object
}

// Args must match the count of function args
func (f *Func) EvalWithMany(args ...PyObject) (PyObject, error) {
	pyArgs := C.PyTuple_New(C.Py_ssize_t(len(args)))

	for pos, pyObject := range args {
		log.Println(pos)
		C.PyTuple_SetItem(pyArgs, C.Py_ssize_t(pos), pyObject)
	}

	result := C.PyObject_CallObject(f.ptr, pyArgs)
	if result == nil {
		return nil, ErrInvalidFuncEval
	}
	return result, nil
}

func (f *Func) Deinit() {
	f.ptr = nil
	C.Py_DecRef(f.ptr)
	C.free(unsafe.Pointer(f.ptr))
}
