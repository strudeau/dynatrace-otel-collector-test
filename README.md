# Dynatrace OpenTelemetry Collector: Single Collector Solution

## TL;DR

**A production-ready single collector that combines host metrics collection with comprehensive internal telemetry and health monitoring - solving containerization challenges through Docker configuration rather than complex multi-collector setups.**

```bash
# Quick start - get everything running
docker-compose up -d

# Check health
curl http://localhost:13133/health

# View metrics
docker-compose logs -f collector
curl http://localhost:8888/metrics
```

## Design Philosophy

This solution demonstrates that **sophisticated observability doesn't require complex architectures**. By carefully configuring Docker containers and understanding OpenTelemetry Collector internals, we achieve:

- ✅ **Host system monitoring** (CPU, memory metrics from the host)
- ✅ **Collector health monitoring** (internal telemetry via Prometheus endpoint)  
- ✅ **Comprehensive diagnostics** (zPages web interface for troubleshooting)
- ✅ **Container orchestration ready** (health checks for Kubernetes/Docker)
- ✅ **Single deployment** (no dual collectors or external dependencies)

**Key Insight**: The breakthrough was discovering that **privileged container settings interfere with internal telemetry process registration**. By removing privileged access while maintaining host filesystem mounts, both capabilities work together seamlessly.

## Monitoring Capabilities

### 🔍 **Host Metrics Collection**
- **CPU & Memory**: System utilization from host (not container)
- **Collection Interval**: 10-second intervals for real-time monitoring
- **Host Access**: Filesystem mounts provide access without privileged containers

### 📊 **Internal Telemetry** 
- **Prometheus Endpoint**: `http://localhost:8888/metrics` (17 collector performance metrics)
- **Key Metrics**: Export success/failure rates, CPU/memory usage, processing throughput
- **Format**: Industry-standard Prometheus format for monitoring integration

### ⚕️ **Health Monitoring**
- **Health Check**: `http://localhost:13133/health` (simple "healthy/unhealthy" status)
- **Kubernetes Ready**: Compatible with liveness/readiness probes
- **Container Orchestration**: Works with Docker health checks and monitoring systems

### 🔧 **Diagnostic Interface**
- **zPages**: `http://localhost:55679/debug/` (web-based diagnostic interface)
- **Real-time Insights**: Pipeline flow, component status, performance analysis
- **Troubleshooting**: Live debugging without external dependencies

## Quick Start

1. **Start the collector:**
   ```bash
   docker-compose up --build
   ```

2. **View metrics output:**
   ```bash
   docker-compose logs -f collector
   ```

3. **Stop the collector:**
   ```bash
   docker-compose down
   ```

## Endpoint Reference

| **Endpoint** | **Purpose** | **Example Usage** |
|--------------|-------------|-------------------|
| `http://localhost:13133/health` | Health status | `curl http://localhost:13133/health` |
| `http://localhost:8888/metrics` | Internal telemetry | `curl http://localhost:8888/metrics \| grep otelcol` |
| `http://localhost:55679/debug/` | Diagnostic interface | Open in browser for web UI |
| `docker-compose logs -f collector` | Host metrics output | Real-time CPU/memory data |

## Production Readiness

### ✅ **Container Orchestration**
```yaml
# Kubernetes readiness probe
readinessProbe:
  httpGet:
    path: /health
    port: 13133
  initialDelaySeconds: 5
  periodSeconds: 10
```

### ✅ **Monitoring Integration** 
```yaml
# Prometheus scrape config
- job_name: 'otel-collector'
  static_configs:
    - targets: ['localhost:8888']
```

### ✅ **Troubleshooting Ready**
- zPages provide real-time diagnostic capabilities
- Comprehensive logging via debug exporter
- Health endpoints for automated monitoring

## Next Steps

**For Production Deployment:**
1. Replace debug exporter with Dynatrace OTLP HTTP exporter
2. Add `DT_ENDPOINT` and `API_TOKEN` environment variables  
3. Configure additional scrapers (disk, network) as needed
4. Set up Prometheus scraping of internal metrics
5. Integrate health checks with orchestration platform

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - Complete architectural documentation and design decisions
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) - Deep-dive troubleshooting guide and containerization insights  
- [`docs/HEALTH-CHECK-GUIDE.md`](docs/HEALTH-CHECK-GUIDE.md) - Comprehensive health monitoring and endpoint documentation
- [`docs/INTERNAL-TELEMETRY-SOLUTION.md`](docs/INTERNAL-TELEMETRY-SOLUTION.md) - Technical analysis of internal telemetry implementation
- [`CLAUDE.md`](CLAUDE.md) - Development guidance for working with this repository

## Key Technical Achievement

**Problem Solved**: OpenTelemetry Collector internal telemetry failed in containerized environments due to process metric registration conflicts with privileged Docker settings.

**Solution Discovered**: Remove privileged container access (`pid: host`, `privileged: true`, `network_mode: host`) while maintaining host filesystem mounts. This allows internal telemetry to work alongside host metrics collection in a single, simplified deployment.

**Impact**: Eliminates the need for complex dual-collector architectures while providing comprehensive observability capabilities.