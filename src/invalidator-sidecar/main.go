package main

import (
	"context"
	"fmt"
	"os"
	"github.com/segmentio/kafka-go"
)

func main() {
	kafkaBroker := os.Getenv("KAFKA_BROKER")
	topic := os.Getenv("KAFKA_TOPIC")
	cacheDir := "/var/cache/nginx"

	fmt.Printf("Starting Hermes Cache Invalidator Sidecar... \n")
	fmt.Printf("Listening to Kafka Broker: %s, Topic: %s\n", kafkaBroker, topic)

	reader := kafka.NewReader(kafka.ReaderConfig {
		Brokers: []string{kafkaBroker},
		GroupID: "edge-cache-invalidator-group",
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

		// Clear the Cache directory
		// Wipe the directory to guarantee a fresh start
		err = os.RemoveAll(cacheDir)
		if err != nil {
			fmt.Printf("Failed to delete cache: %v\n", err)
		} else {
			// Recreate the empty directory so NGINX can continue to write to it
			os.MkdirAll(cacheDir, 0755)
			fmt.Println("Successfully purged NGINX cache directory!")
		}
	}
}