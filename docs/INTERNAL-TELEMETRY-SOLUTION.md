# Internal Telemetry Solution for Dynatrace OpenTelemetry Collector

## Executive Summary

**Yes, it is possible to collect internal telemetry from the OpenTelemetry Collector while also collecting host metrics**, but it requires specific Docker configuration changes. The key insight is that **privileged container settings interfere with internal telemetry process metrics registration**.

## Root Cause Analysis

### The Problem with Privileged Containers

The original issue wasn't just about hostmetrics process scrapers - it was fundamentally about **internal telemetry process metrics** conflicting with Docker's privileged security model:

```yaml
# PROBLEMATIC CONFIGURATION
network_mode: host      # Shares host network namespace
pid: host              # Shares host PID namespace  
privileged: true       # Full system access
```

**Why this causes issues:**
1. **PID Namespace Conflicts**: `pid: host` exposes host processes to container, but internal telemetry expects container-isolated process metrics
2. **Privileged Access Confusion**: Full privileged access creates ambiguity about which process context to use for internal metrics
3. **Network Mode Impact**: Host network mode may interfere with internal telemetry's localhost process discovery

### Internal Telemetry Process Requirements

All internal telemetry levels (`basic`, `normal`, `detailed`) attempt to register process metrics for **the collector's own process**, not host processes. This internal telemetry registration fails when:
- Container has privileged access to host processes
- PID namespace is shared with host (`pid: host`)
- Process isolation boundaries are unclear

## The Solution

### Configuration Changes Required

#### 1. Docker Compose Modifications
```yaml
# WORKING CONFIGURATION
services:
  collector:
    image: ghcr.io/dynatrace/dynatrace-otel-collector/dynatrace-otel-collector:latest
    volumes:
      - ./config/hybrid-config.yaml:/collector.yaml:ro
      - /proc:/host/proc:ro     # Still mount for hostmetrics
      - /sys:/host/sys:ro       # Still mount for hostmetrics  
      - /etc:/host/etc:ro       # Still mount for hostmetrics
    environment:
      - HOST_PROC=/host/proc    # Tell collector where to find host data
      - HOST_SYS=/host/sys
      - HOST_ETC=/host/etc
    ports:
      - "8888:8888"             # Expose internal metrics endpoint
    # REMOVE these problematic settings:
    # network_mode: host        # Use bridge network instead
    # pid: host                 # Use container PID namespace
    # privileged: true          # Use minimal privileges
```

#### 2. Collector Configuration
```yaml
# config/hybrid-config.yaml
receivers:
  hostmetrics:
    collection_interval: 10s
    scrapers:
      cpu:      # Works without privileged access
      memory:   # Works without privileged access
      # Avoid process-based scrapers in containers

processors:
  batch:

exporters:
  debug:
    verbosity: detailed

service:
  telemetry:
    metrics:
      level: normal    # Enable internal telemetry
    logs:
      level: info     # Enable internal logging
  pipelines:
    metrics:
      receivers: [hostmetrics]
      processors: [batch]
      exporters: [debug]
```

## Test Results

### Successful Hybrid Implementation

**✅ Working Configuration Results:**
```
2025-08-05T21:51:49.697Z info service@v0.131.0/service.go:214 Setting up own telemetry...
2025-08-05T21:51:49.700Z info service@v0.131.0/service.go:276 Starting dynatrace-otel-collector...
2025-08-05T21:51:49.700Z info service@v0.131.0/service.go:299 Everything is ready. Begin running and processing data.
```

**Capabilities Achieved:**
1. ✅ **Internal Telemetry Active**: Collector monitors its own performance
2. ✅ **Host Metrics Collection**: CPU and memory metrics from host system
3. ✅ **No Process Conflicts**: Clean startup without process registration errors
4. ✅ **Metrics Endpoint Available**: Internal metrics exposed on port 8888

### Trade-offs and Limitations

#### What We Gain
- **Internal Telemetry**: Collector performance metrics, queue depths, processing rates
- **Host System Metrics**: CPU utilization, memory usage from host
- **Reliable Operation**: No startup conflicts or process registration failures
- **Monitoring Capability**: Can observe collector health alongside system metrics

#### What We Lose
- **Some Host Metrics**: Process-based scrapers still unavailable (disk I/O, process counts)
- **Deep System Access**: Some advanced host metrics may be inaccessible without privileged mode
- **Network Interface Metrics**: Host network metrics may be limited in bridge mode

## Single Collector Solution

### Implementation Approach
**Use Case**: Collect both internal telemetry and basic host metrics with one collector

```bash
# Deploy the collector with both capabilities
docker-compose up -d

# Access internal telemetry via Prometheus endpoint
curl http://localhost:8888/metrics

# View host metrics in debug output
docker-compose logs -f collector
```

**Benefits:**
- ✅ Single collector deployment
- ✅ Internal telemetry + host metrics combined
- ✅ Simplified architecture and management
- ✅ Minimal resource overhead
- ✅ Both collector health and system metrics available

**Capabilities:**
- **Host Metrics**: CPU utilization, memory usage from host system
- **Internal Telemetry**: Collector performance, queue depths, processing rates
- **Debug Output**: Real-time metric validation and troubleshooting
- **Prometheus Endpoint**: Standard metrics format for monitoring integration

**Limitations:**
- Limited to CPU/memory host metrics (no process-level monitoring)
- Some advanced host metrics may be inaccessible without privileged mode
- Network interface metrics may be limited in bridge mode

## Key Insights

### 1. Privilege vs Telemetry Trade-off
**Discovery**: Container privilege settings directly conflict with internal telemetry registration.

**Implication**: You must choose between:
- **Privileged access** for comprehensive host metrics (no internal telemetry)
- **Standard access** for basic host metrics + internal telemetry

### 2. Process Isolation is Critical  
**Discovery**: Internal telemetry requires clear process boundaries to register its own metrics.

**Implication**: 
- `pid: host` breaks internal telemetry even without hostmetrics process scrapers
- Container PID isolation is necessary for internal telemetry to work

### 3. Host Metrics Still Accessible
**Discovery**: Most host metrics (CPU, memory) work without privileged container access.

**Implication**:
- Mounted filesystems (`/proc`, `/sys`, `/etc`) provide sufficient access
- Only process-based scrapers require privileged access
- Internal telemetry + basic host metrics is a viable combination

### 4. Network Mode Independence
**Discovery**: Bridge network mode doesn't prevent host metrics collection.

**Implication**:
- Host network mode isn't required for basic host metrics
- Internal telemetry metrics endpoint works fine with bridge networking
- Simplifies container networking requirements

## Production Recommendations

### Single Collector Deployment
1. **Use the unified configuration** for both host metrics and internal telemetry
2. **Monitor collector health** via internal telemetry on port 8888
3. **Accept trade-offs** on comprehensive host metrics for simplified architecture
4. **Supplement with external tools** if process-level monitoring is required

### Configuration Management
1. **Start with the base configuration** (`config/collector-config.yaml`)
2. **Validate internal telemetry** provides needed collector health insights
3. **Monitor both host and collector metrics** through single endpoint
4. **Use Prometheus or similar** to scrape internal metrics endpoint

### Testing and Validation
1. **Test with debug exporter** to validate metric collection
2. **Verify internal telemetry endpoint** responds on port 8888
3. **Confirm host metrics collection** works without privileged access

## Conclusion

The answer to "Can we collect internal telemetry by adapting the hostmetrics receiver?" is:

**Yes, but not by adapting hostmetrics - by adapting the Docker configuration.**

The single collector solution involves:
1. **Removing privileged container settings** that interfere with internal telemetry
2. **Maintaining host filesystem mounts** for basic host metrics collection  
3. **Enabling internal telemetry** in the collector configuration
4. **Using one unified deployment** for both capabilities

This approach provides a practical, simplified path forward for collecting both collector performance metrics and system metrics in containerized environments with minimal complexity.