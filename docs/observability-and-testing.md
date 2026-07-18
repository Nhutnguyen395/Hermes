# 📊 Observability & Load Testing

To manage and validate a distributed network, Hermes implements a comprehensive Mission Control observability stack and automated load testing suite.

## 👁️ The Telemetry Pipeline (Prometheus & Grafana)
Hermes utilizes the `kube-prometheus-stack` to scrape, store, and visualize metrics across the cluster.
* **Dynamic Service Discovery:** Instead of hardcoding IPs, Hermes uses Kubernetes `ServiceMonitors`. By applying the `layer: edge-proxy` label to our Edge Services, Prometheus automatically discovers and scrapes new PoPs as the network scales globally.
* **Origin Metrics:** The Spring Boot Origin utilizes the **Micrometer Prometheus Registry** to expose JVM health, memory usage, and HTTP request durations via the `/actuator/prometheus` endpoint.

## 📝 NGINX Log Exporter Sidecar
Open-source NGINX does not natively expose Cache Hit/Miss metrics. Hermes engineers around this limitation using a second sidecar pattern:
1. **Custom Logging:** NGINX is configured to append the `$upstream_cache_status` (HIT, MISS, EXPIRED) to its `access.log`.
2. **Log Volume Sharing:** A shared `emptyDir` volume mounts the logs between NGINX and the `prometheus-nginxlog-exporter` sidecar.
3. **Real-Time Parsing:** The sidecar tails the log file, counts the occurrences of HITs and MISSes, and exposes them on port `4040` for Prometheus to scrape.
4. **Grafana Visualization:** Using PromQL (e.g., `sum by (upstream_cache_status) (rate(hermes_cdn_http_response_count_total[5m]))`), these metrics are visualized in Grafana to prove the CDN's offload efficiency.

## 🚦 Automated Load Testing & Validation
Hermes includes a dedicated load testing suite to validate architectural resilience under heavy concurrent traffic.
* **Simulated Traffic:** The suite generates 50 concurrent virtual users over a sustained duration.
* **Geo-Router Validation:** The script randomizes the `X-User-Region` header, proving the Gateway API successfully splits traffic between the US and EU Edge PoPs.
* **Rate-Limit Validation:** The script spoofs randomized IP addresses to intentionally trigger the NGINX Token-Bucket rate limiter. Grafana telemetry confirms the Edge successfully drops excess traffic (HTTP 503) before it reaches the Origin.