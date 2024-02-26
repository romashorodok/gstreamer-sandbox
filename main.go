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

	// name := "John" // Update with the desired name
	// pName = C.CString(name)
	// defer C.free(unsafe.Pointer(pName))
	// // pNameObj := C.PyUnicode_DecodeFSDefault(pName)
	// // defer C.Py_DecRef(pNameObj)
	//
	// pySize := C.Py_ssize_t(1)
	// log.Println(pySize)
	//
	// // pArgs := C.PyTuple_Pack(C.Py_ssize_t(1), pNameObj)
	// // defer C.Py_DecRef(pArgs)
	//
	// // // Create a tuple to hold the arguments
	// // pArgs := C.PyTuple_Pack(1, pNameObj)
	// // defer C.Py_DecRef(pArgs)
	//
	// log.Printf("%+v", greetFunc)
	//
	// pArgs := C.PyTuple_New(pySize)
	// defer C.Py_DecRef(pArgs)
	//
	// // C.PyTuple_SetItem(pArgs, C.Py_ssize_t(0), C.PyBytes_FromString(pName))
	//
	// // https://docs.python.org/3/c-api/unicode.html#c.PyUnicode_FromString
	// C.PyTuple_SetItem(pArgs, C.Py_ssize_t(0), C.PyUnicode_FromString(pName))
	//
	// // https://docs.python.org/3/c-api/call.html#c.PyObject_CallObject
	// pResult := C.PyObject_CallObject(greetFunc, pArgs)
	// defer C.Py_DecRef(pResult)

	xor_bytes := C.PyObject_GetAttrString(pModule, C.CString("xor_bytes"))
	if greetFunc == nil {
		log.Fatal("Failed to find greet function")
	}
	defer C.Py_DecRef(greetFunc)

	// log.Println(xor_bytes)
	inputBytes := []byte{'a', 'b', 'c'}

	// Create a Python bytes object
	pInputBytes := C.PyBytes_FromStringAndSize((*C.char)(unsafe.Pointer(&inputBytes[0])), C.Py_ssize_t(len(inputBytes)))
	defer C.Py_DecRef(pInputBytes)

	result := C.PyObject_CallOneArg(xor_bytes, pInputBytes)
	if result == nil {
		handleError()
		return
	}
	defer C.Py_DecRef(result)

	// Retrieve the result as a byte slice
	// var outputBytes []byte
	// cOutputBytes := C.PyBytes_AsString(result)
	outputSize := C.PyBytes_Size(result)
	cOutputBytes := C.PyBytes_AsString(result)
	outputBytes := C.GoBytes(unsafe.Pointer(cOutputBytes), C.int(outputSize))

	// log.Println(unsafe.Pointer(cOutputBytes))

	// outputBytes = C.GoBytes(unsafe.Pointer(cOutputBytes), outputSize)

	// log.Println(outputSize)
	// log.Println(cOutputBytes)

	log.Printf("Input Bytes: %v", inputBytes)
    log.Println(string(outputBytes))
	// log.Printf("%s", outputBytes)
	// log.Printf("Output Bytes (after XOR): %v", string(outputBytes))

	// Handle any errors
	handleError()
}

func handleError() {
	if C.PyErr_Occurred() != nil {
		C.PyErr_Print()
	}
}
