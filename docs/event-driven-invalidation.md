# ⚡ Event-Driven Cache Invalidation

One of the hardest problems in distributed systems is cache invalidation. If a user updates an asset at the Origin, the Edge PoPs must instantly drop the old version. Hermes solves this using a modern, event-driven "Push" architecture rather than a traditional, latency-heavy "Pull" (polling) model.

## 📡 The Broadcast Architecture (Apache Kafka)
Hermes utilizes **Apache Kafka** (deployed via the Strimzi Operator in KRaft mode) as the central event broker.
1. When an asset is updated, the Spring Boot Origin publishes a JSON event (e.g., `{"assetId": "secure-image-1"}`) to the `cache-invalidation-events` topic.
2. Kafka acts as a global broadcaster.
3. Every Edge PoP runs a custom Go (Golang) sidecar. To ensure *every* PoP receives the message (rather than load-balancing the message among them), each Go sidecar dynamically generates a unique Kafka `GroupID` using its Kubernetes Pod hostname.

## 🪚 The Invalidator (Go Sidecar)
Wiping an entire cache during a single asset update causes a "Cache Stampede," overwhelming the Origin. Hermes implements a "Scalpel" approach to perform targeted purges.

Because standard NGINX containers do not natively communicate with Kafka, Hermes uses the **Kubernetes Sidecar Pattern**:
* **Shared Memory:** The NGINX container and the Go container share an `emptyDir` volume mounted at `/var/cache/nginx`.
* **MD5 Hashing:** NGINX is configured to use the URL path as the `proxy_cache_key`. When NGINX caches a file, it hashes this key using MD5 and stores it in a nested directory structure (e.g., `/var/cache/nginx/7/4d/8b1a9953c4611296a827abf8c47804d7`).
* **Targeted Deletion:** When the Go sidecar receives the Kafka event, it parses the JSON, calculates the exact same MD5 hash for the asset, navigates the shared volume, and deletes *only* that specific file.

The next time a user requests that specific asset, NGINX registers a Cache MISS and fetches the fresh version from the Origin, while all other cached assets remain perfectly intact.