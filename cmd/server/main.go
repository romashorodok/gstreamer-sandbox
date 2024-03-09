package main

/*
#cgo pkg-config: pipelines-1.0
#cgo pkg-config: proxypipe-1.0
#cgo LDFLAGS: -lstdc++
#include "pipelines.h"
#include "proxy_pipe.h"
*/
import "C"

import (
	"fmt"
	"net"
	"unsafe"
)

func udpServer(pipeline unsafe.Pointer) {
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
		// log.Println("On udp server")

		b := C.CBytes(buffer)
		defer C.free(b)
		C.write_proxy_pipe(pipeline, b, C.int(len(buffer)))
	}
}

func main() {
	C.setup()
	pipeName := C.CString("dynamic-pipe-name")
	pipeline := C.new_proxy_pipe_rtp_vp8(pipeName)
	defer C.delete_proxy_pipe(pipeline)
	C.start_proxy_pipe(pipeline)

	udpServer(pipeline)
}
