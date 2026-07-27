import os
import json
from confluent_kafka import Producer

# Defaulting to localhost for local Docker-based Kafka,
# but configurable for Kubernetes (e.g., kafka-cluster-kafka-bootstrap:9092)
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_PURGE_TOPIC = os.getenv("KAFKA_PURGE_TOPIC", "cache-purge-events")

producer_config = {'bootstrap.servers': KAFKA_BROKER}
producer = Producer(producer_config)

def publish_purge_event(cache_key: str):
    """
    Publishes an invalidation event to the kafka topic.
    The Hermes Edge Nodes are subscribed to this topic and will execute the actual Nginx purge.
    """
    payload = {
        "key": cache_key,
        "action": "PURGE",
        "source": "sentinel-agent"
    }

    def delivery_report(err, msg):
        if err is not None:
            print(f"[Executor] Message delivery failed: {err}")
        else:
            print(f"[Executor] Successfully published purge event to {msg.topic()} for key: {cache_key}")

    producer.produce(
        topic=KAFKA_PURGE_TOPIC,
        value=json.dumps(payload).encode('utf-8'),
        callback=delivery_report
    )

    producer.flush(timeout=2.0)