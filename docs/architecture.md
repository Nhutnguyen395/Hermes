# 🏛️ System Architecture

The Hermes CDN Simulator is designed to mimic the physical and logical architecture of a real-world Content Delivery Network (CDN) like Cloudflare or Fastly, scaled down to run locally on a Kubernetes cluster.

## 🌍 Global Topology Simulation
In a real CDN, servers are physically located in distinct geographic regions. To simulate this locally, Hermes utilizes **Kubernetes (Kind)** with custom node labels:
* `topology.kubernetes.io/region=core-origin`: Represents the central data center housing the main database and heavy backend services.
* `topology.kubernetes.io/region=us-east`: Represents a Point of Presence (PoP) in North America.
* `topology.kubernetes.io/region=eu-west`: Represents a Point of Presence (PoP) in Europe.

Using Kubernetes `nodeSelector` and `nodeAffinity`, we enforce strict scheduling so that Edge Proxy Pods only run in their designated geographic regions.

## 🔄 The Life of a Request (Traffic Flow)
1. **User Request:** A user makes an HTTP GET request with a simulated geographic header (`X-User-Region: US`).
2. **Layer 7 Geo-Routing:** The request hits the NGINX Gateway Fabric (Gateway API). The `HTTPRoute` evaluates the header and proxies the traffic to the `us-edge-service`.
3. **Edge Security:** The NGINX Edge Proxy evaluates the request against a Token-Bucket Rate Limiter (1 req/sec).
4. **Cache Evaluation:**
    * **Cache HIT:** NGINX serves the asset from its local `emptyDir` volume in milliseconds, completely shielding the Origin.
    * **Cache MISS:** NGINX forwards the request to the Origin.
5. **Origin Processing:** The Spring Boot (Java 21) Origin validates the Auth0 RS256 JWT signature. If valid, it processes the request (simulating a 3-second database lookup), returns the asset, and NGINX caches it for future users.

## 🧠 Control Plane vs. Data Plane
Hermes strictly adheres to the modern separation of concerns:
* **Control Plane:** Components like the `ngf-nginx-gateway-fabric` and `strimzi-kafka-operator` do not handle web traffic. They monitor Kubernetes manifests and dynamically configure the infrastructure.
* **Data Plane:** The dynamically generated NGINX Pods and Spring Boot applications handle the actual byte-level routing and processing.