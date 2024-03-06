package cython

/*
#cgo pkg-config: python3
#cgo LDFLAGS: -lpython3.12
#include <Python.h>
*/
import "C"

import (
	"errors"
	"fmt"
	"log"
	"log/slog"
	"os"
	"time"
	"unsafe"
	// "arena"
)

const (
	_OK                   = 0
	_SYS_PATH_OBJECT_NAME = "path"
)

var (
	ErrUnableAddModule  = errors.New("")
	ErrUnableLoadModule = errors.New("unable load module")
)

type runtime struct {
	log *slog.Logger
}

type InitParams struct {
	ModulePath []string
}

func (r *runtime) preInit() {
	config := new(C.PyPreConfig)
	configPtr := (*C.PyPreConfig)(unsafe.Pointer(config))
	C.PyPreConfig_InitPythonConfig(configPtr)
	defer C.free(unsafe.Pointer(configPtr))

	// https://docs.python.org/3/c-api/init_config.html#c.PyPreConfig.allocator
	config.allocator = C.PYMEM_ALLOCATOR_MALLOC

	result := C.Py_PreInitialize(configPtr)
	log.Println(C.GoString(result.err_msg))
}

func (r *runtime) Init(params InitParams) {
	// r.preInit()

	// config := new(C.PyConfig)
	// configPtr := (*C.PyConfig)(unsafe.Pointer(config))
	// C.PyConfig_InitPythonConfig(configPtr)

	//
	// config.module_search_paths_set = 1
	// moduleSearchPaths := (*C.PyWideStringList)(unsafe.Pointer(&config.module_search_paths))
	//
	// for pos, modulePath := range params.ModulePath {
	// 	modulePathPtr := (*C.wchar_t)(unsafe.Pointer(C.CString(modulePath)))
	//
	// 	result := C.PyWideStringList_Insert(moduleSearchPaths, C.Py_ssize_t(pos), modulePathPtr)
	// 	log.Println(C.GoString(result.err_msg))
	// 	// C.free(modulePathPtr)
	// }
	//
	// r.log.Info("Cython init runtime")

	C.Py_Initialize()
	// result := C.Py_InitializeFromConfig(configPtr)
	// log.Println(C.GoString(result.err_msg))
	ticker := time.NewTicker(time.Millisecond * 5)
	for {
		select {
		case <-ticker.C:
			if ok := int(C.Py_IsInitialized()); ok != 0 {
				r.log.Info(fmt.Sprintf("Cython done init with %d", ok))
				return
			}
		}
	}
}

func (r *runtime) Deinit() {
	r.log.Info("[Cython] Deinit runtime")
	C.Py_Finalize()
}

func (r *runtime) AddModule(dirPath string) error {
	r.log.Info(fmt.Sprintf("Add `%s` into sys.path modules", dirPath))

	sysPathObjectName := C.CString(_SYS_PATH_OBJECT_NAME)
	defer C.free(unsafe.Pointer(sysPathObjectName))

	sys_path := C.PySys_GetObject(sysPathObjectName)
	log.Println(sys_path)

	//    log.Println(sys_path)

	pathStrPtr := C.CString(dirPath)
	defer C.free(unsafe.Pointer(pathStrPtr))

	pathPyObj := C.PyUnicode_DecodeFSDefault(pathStrPtr)
	defer C.Py_DecRef(pathPyObj)

	var result int = int(C.PyList_Insert(sys_path, 0, pathPyObj))
	if result != _OK {
		return ErrUnableAddModule
	}
	return nil
}

func (r *runtime) LoadModule(name string) (*Module, error) {
	namePtr := C.CString(name)
	defer C.free(unsafe.Pointer(namePtr))
	module := C.PyImport_ImportModule(namePtr)
	if module == nil {
		return nil, errors.Join(ErrUnableLoadModule, fmt.Errorf("module: %s", name))
	}
	return &Module{ptr: module}, nil
}

func NewRuntime() *runtime {
	return &runtime{
		log: slog.New(slog.NewJSONHandler(os.Stdout, nil)),
	}
}

type Module struct {
	ptr *C.struct__object
}

func (m *Module) Deinit() {
	m.ptr = nil
	C.Py_DecRef(m.ptr)
	C.free(unsafe.Pointer(m.ptr))
}

func (m *Module) GetFunc(name string) (*Func, error) {
	namePtr := C.CString(name)
	defer C.free(unsafe.Pointer(namePtr))

	f := C.PyObject_GetAttrString(m.ptr, namePtr)
	if f == nil {
		return nil, errors.Join(fmt.Errorf("func: %s", name))
	}

	return &Func{ptr: f}, nil
}
