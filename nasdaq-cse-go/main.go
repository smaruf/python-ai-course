// Package main is the entry point for the Gold Derivatives Trading Simulator
package main

import (
	"log"
	"os"
	"os/exec"
)

func main() {
	// Change to the project directory and run the server
	cmd := exec.Command("go", "run", "./cmd/server")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	
	if err := cmd.Run(); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}