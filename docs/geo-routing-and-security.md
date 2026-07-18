# 🛡️ Geo-Routing & Zero-Trust Security

Hermes implements advanced traffic routing and security at the "Edge" of the network to protect the core Origin from malicious traffic and DDoS attacks.

## 🗺️ Layer 7 Geo-Routing (Kubernetes Gateway API)
Historically, Kubernetes routing was handled by the monolithic `Ingress` API. Hermes utilizes the modern **Kubernetes Gateway API** (via NGINX Gateway Fabric) to decouple infrastructure from application routing.

Instead of relying on BGP Anycast (which routes traffic at the network hardware level), Hermes acts as a Layer 7 Application Router.
* I define a `Gateway` listening on an unprivileged port (`8080`).
* I define an `HTTPRoute` that acts as a programmable router. It reads the `X-User-Region` HTTP header and routes traffic to specific backend services (`us-edge-service` or `eu-edge-service`).

## 🚦 Edge Rate Limiting (Token-Bucket Algorithm)
To mitigate DDoS attacks and abusive bots, Hermes enforces Rate Limiting directly at the Edge PoPs before traffic can reach the Origin.
* **Mechanism:** NGINX is configured with a `limit_req_zone` utilizing a 10MB memory zone to track client IP addresses (`$binary_remote_addr`).
* **Thresholds:** The limit is strictly set to **1 request per second** with a burst allowance of 2 (to handle rapid double-clicks).
* **Result:** Any IP exceeding this limit is immediately dropped at the Edge with an `HTTP 503 Service Unavailable`, shielding the Origin's CPU and database connections.

## 🔐 Zero-Trust JWT Validation (Asymmetric RS256)
Hardcoding symmetric API keys is an anti-pattern. Hermes utilizes **Asymmetric Encryption (RS256)** via Auth0 to secure the Origin.
1. The Spring Boot Origin is configured as an OAuth2 Resource Server.
2. On startup, it dynamically fetches the Auth0 Public Keys from the `/.well-known/jwks.json` endpoint.
3. When a request arrives (even if it bypassed the Edge proxy), the Origin cryptographically verifies the `Authorization: Bearer <TOKEN>` signature.
4. **Zero-Trust:** If the Edge Proxy is compromised, the Origin remains secure because it validates every single request independently.