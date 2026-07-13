package main

import (
	"context"
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"github.com/segmentio/kafka-go"
)

type InvalidationEvent struct {
	AssetID string `json:"assetId"`
}

func main() {
	kafkaBroker := os.Getenv("KAFKA_BROKER")
	topic := os.Getenv("KAFKA_TOPIC")
	cacheDir := "/var/cache/nginx"

	// Get the unique kubernetes Pod Name (Hostname)
	hostname, _ := os.Hostname()
	uniqueGroupID := "invalidator-" + hostname

	fmt.Printf("Starting Hermes Targeted Cache Invalidator... \n")
	fmt.Printf("Pod: %s | Listening to Topic: %s\n", hostname, topic)

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

		// Parse the JSON
		var event InvalidationEvent
		err = json.Unmarshal(msg.Value, &event)
		if err != nil {
			fmt.Printf("Failed to parse JSON: %v\n", err)
		}

		cacheKey := "/api/v1/assets/" + event.AssetID

		// Compute the MD5 Hash
		hash := md5.Sum([]byte(cacheKey))
		hashStr := hex.EncodeToString(hash[:])

		// Calculate the NGINX folder structure based on levels=1:2
		// Last character of hash
		dir1 := hashStr[len(hashStr)-1:]
		// Next two character from the end
		dir2 := hashStr[len(hashStr)-3 : len(hashStr)-1]

		// Build the full path to the specific cache file
		targetFile := filepath.Join(cacheDir, dir1, dir2, hashStr)

		// Delete only the specific file
		err = os.Remove(targetFile)
		if err != nil {
			if os.IsNotExist(err) {
				fmt.Printf("Cache file for %s not found (already purged or never cached).\n", event.AssetID)
			} else {
				fmt.Printf("Failed to delete cache file: %v\n", err)
			}
		} else {
			fmt.Printf("SUCCESS: Targeted purge completed for %s!\n", event.AssetID)
		}
	}
}