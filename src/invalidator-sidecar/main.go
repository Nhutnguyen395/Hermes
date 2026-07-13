package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"github.com/segmentio/kafka-go"
)

func main() {
	kafkaBroker := os.Getenv("KAFKA_BROKER")
	topic := os.Getenv("KAFKA_TOPIC")
	cacheDir := "/var/cache/nginx"

	// Get the unique kubernetes Pod Name (Hostname)
	hostname, err := os.Hostname()
	if err != nil {
		hostname = "unknown-host"
	}

	// Create a UNIQUE group ID for this specific pod
	uniqueGroupID := "invalidator-" + hostname

	fmt.Printf("Starting Hermes Cache Invalidator Sidecar... \n")
	fmt.Printf("Listening to Kafka Broker: %s, Topic: %s\n", kafkaBroker, topic)

	// Use the unique group id
	reader := kafka.NewReader(kafka.ReaderConfig {
		Brokers: []string{kafkaBroker},
		GroupID: uniqueGroupID,
		Topic: topic,
		MinBytes: 10e3, // 10KB
		MaxBytes: 10e6, // 10MB
	})

	defer reader.Close()

	for {
		// ReadMessage blocks until a new message arrives from Kafka
		msg, err := reader.ReadMessage(context.Background())

		if err != nil {
			fmt.Printf("Error reading message: %v\n", err)
			continue
		}

		fmt.Printf("Received Invalidation Event: %s\n", string(msg.Value))

		// Safely delete the contents of the cache director
		entries, err := os.ReadDir(cacheDir)
		if err != nil {
			fmt.Printf("Failed to read cache directory: %v\n", err)
			continue
		}

		for _, entry := range entries {
			err := os.RemoveAll(filepath.Join(cacheDir, entry.Name()))
			if err != nil {
				fmt.Printf("Failed to delete %s: %v\n", entry.Name(), err)
			}
		}
		fmt.Println("Successfully purged NGINX cache contents!")
	}
}