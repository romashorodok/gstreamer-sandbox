package cython

/*
#cgo pkg-config: python3
#cgo LDFLAGS: -lpython3.12
#include <Python.h>
*/
import "C"

import "unsafe"

type PyObject = *C.struct__object

func ptrToPyObject(ptr unsafe.Pointer) PyObject {
	return (PyObject)(ptr)
}

func Bytes(data []byte) PyObject {
	return C.PyBytes_FromStringAndSize((*C.char)(unsafe.Pointer(&data[0])), C.Py_ssize_t(len(data)))
}

func FreePyObject(obj PyObject) {
	C.Py_DecRef(obj)
}
