package main

import (
	"fmt"
	"net"
	"os"

	"github.com/romashorodok/cython-test/rtp/cython"
)

func udpServer(writer *cython.Func) {
	// Define the server address (localhost) and port
	serverAddr, err := net.ResolveUDPAddr("udp", ":34788")
	if err != nil {
		fmt.Println("Error resolving address:", err)
		return
	}
	conn, err := net.ListenUDP("udp", serverAddr)
	if err != nil {
		fmt.Println("Error listening:", err)
		return
	}
	defer conn.Close()
	buffer := make([]byte, 1024)

	for {
		_, err := conn.Read(buffer)
		// Read data from the client
		if err != nil {
			fmt.Println("Error reading from UDP:", err)
			continue
		}

        writer.EvalWithMany(cython.Bytes(buffer))
		// log.Println(n, buffer)
	}
}

func main() {

	cythonRt := cython.NewRuntime()

	currentDir, err := os.Getwd()
	if err != nil {
		panic(err)
	}

	cythonRt.Init(cython.InitParams{
		ModulePath: []string{
			currentDir,
		},
	})
	defer cythonRt.Deinit()
	err = cythonRt.AddModule(currentDir)

	//
	// module, err := cythonRt.LoadModule("greetmodule")
 //    log.Println("mod ", module, err)
	// //
	// fn, err := module.GetFunc("second")
	// log.Println("fn ", fn, err)
	// //
	// inputBytes := make([]byte, 100, 100)
	// pInputBytes0 := cython.Bytes(inputBytes)
	// // pInputBytes1 := cython.Bytes(inputBytes)
	// //
	// result, err := fn.EvalWithMany(pInputBytes0)
	// cython.FreePyObject(result)
	// log.Println(result, err)

	// fn.Deinit()
	// fn.Eval()
	// udpServer(fn)
}
