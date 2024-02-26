package main

/*
#cgo pkg-config: python3
#cgo LDFLAGS: -lpython3.12
#include <Python.h>
*/
import "C"

import (
	"log"
	"os"
	"unsafe"
)

func main() {
	C.Py_Initialize()
	defer C.Py_Finalize()

	// Get the current directory
	currentDir, err := os.Getwd()
	if err != nil {
		log.Fatalf("Error getting current directory: %v", err)
	}

	// Add the current directory to sys.path
	sysPath := C.PySys_GetObject(C.CString("path"))
	currentDirStr := C.CString(currentDir)
	defer C.free(unsafe.Pointer(currentDirStr))

	// Convert the currentDirStr to a Python object
	pCurrentDirStr := C.PyUnicode_DecodeFSDefault(currentDirStr)
	defer C.Py_DecRef(pCurrentDirStr)

	// Insert the current directory to sys.path
	C.PyList_Insert(sysPath, 0, pCurrentDirStr)

	// Import the compiled Python module
	pName := C.CString("greetmodule") // Update with your actual module name
	defer C.free(unsafe.Pointer(pName))

	pModule := C.PyImport_ImportModule(pName)
	if pModule == nil {
		handleError()
		return
	}
	defer C.Py_DecRef(pModule)

	// Call the greet function
	greetFunc := C.PyObject_GetAttrString(pModule, C.CString("greet"))
	if greetFunc == nil {
		log.Fatal("Failed to find greet function")
	}
	defer C.Py_DecRef(greetFunc)

	// Convert the name to a Python string
	// name := "John" // Update with the desired name
	// pName = C.CString(name)
	// defer C.free(unsafe.Pointer(pName))
	// pNameObj := C.PyUnicode_DecodeFSDefault(pName)
	// defer C.Py_DecRef(pNameObj)

	name := "John" // Update with the desired name
	pName = C.CString(name)
	defer C.free(unsafe.Pointer(pName))
	// pNameObj := C.PyUnicode_DecodeFSDefault(pName)
	// defer C.Py_DecRef(pNameObj)

	pySize := C.Py_ssize_t(1)
	log.Println(pySize)

	// pArgs := C.PyTuple_Pack(C.Py_ssize_t(1), pNameObj)
	// defer C.Py_DecRef(pArgs)

	// // Create a tuple to hold the arguments
	// pArgs := C.PyTuple_Pack(1, pNameObj)
	// defer C.Py_DecRef(pArgs)

	log.Printf("%+v", greetFunc)

	pArgs := C.PyTuple_New(pySize)
	defer C.Py_DecRef(pArgs)

	// C.PyTuple_SetItem(pArgs, C.Py_ssize_t(0), C.PyBytes_FromString(pName))

	// https://docs.python.org/3/c-api/unicode.html#c.PyUnicode_FromString
	C.PyTuple_SetItem(pArgs, C.Py_ssize_t(0), C.PyUnicode_FromString(pName))

	// https://docs.python.org/3/c-api/call.html#c.PyObject_CallObject
	pResult := C.PyObject_CallObject(greetFunc, pArgs)
	defer C.Py_DecRef(pResult)

	// Handle any errors
	handleError()
}

func handleError() {
	if C.PyErr_Occurred() != nil {
		C.PyErr_Print()
	}
}
