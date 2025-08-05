# Health Check and Monitoring Guide

## Overview

The Dynatrace OpenTelemetry Collector provides comprehensive health checking and monitoring capabilities through built-in extensions and telemetry features.

## Available Health & Monitoring Endpoints

### 1. Health Check Extension (Port 13133)

**Purpose**: Provides a simple HTTP health check endpoint for container orchestration and monitoring systems.

**Endpoint**: `http://localhost:13133/health`

**Configuration**:
```yaml
extensions:
  health_check:
    endpoint: "0.0.0.0:13133"
    path: "/health" 
    response_body:
      healthy: "Collector is healthy"
      unhealthy: "Collector is unhealthy"
```

**Usage**:
```bash
# Check collector health
curl http://localhost:13133/health

# Response when healthy: "Collector is healthy"
# Response when unhealthy: "Collector is unhealthy"
```

**Use Cases**:
- Kubernetes liveness/readiness probes
- Docker health checks
- Load balancer health monitoring
- Container orchestration platforms

### 2. Internal Telemetry Metrics (Port 8888)

**Purpose**: Exposes internal collector performance metrics in Prometheus format.

**Endpoint**: `http://localhost:8888/metrics`

**Key Metrics Available**:
- `otelcol_exporter_sent_metric_points_total`: Successfully exported metrics
- `otelcol_exporter_send_failed_metric_points_total`: Failed export attempts
- `otelcol_process_cpu_seconds_total`: Collector CPU usage
- `otelcol_process_memory_rss_bytes`: Collector memory usage
- `otelcol_receiver_accepted_metric_points_total`: Metrics received
- Pipeline throughput and processing metrics

**Configuration**:
```yaml
service:
  telemetry:
    metrics:
      level: normal
      readers:
        - pull:
            exporter:
              prometheus:
                host: '0.0.0.0'
                port: 8888
```

**Usage**:
```bash
# Get all internal metrics
curl http://localhost:8888/metrics

# Count available metrics
curl -s http://localhost:8888/metrics | grep "^# HELP" | wc -l

# Check specific metrics
curl -s http://localhost:8888/metrics | grep "otelcol_process"
```

### 3. zPages Diagnostic Interface (Port 55679)

**Purpose**: Provides web-based diagnostic interface for debugging and monitoring collector internals.

**Base URL**: `http://localhost:55679/debug/`

**Available Pages**:
- **ServiceZ** (`/debug/servicez`): Overview of collector services and runtime information
- **PipelineZ** (`/debug/pipelinez`): Pipeline insights, components, and data flow
- **ExtensionZ** (`/debug/extensionz`): List of active extensions
- **FeatureZ** (`/debug/featurez`): Feature gates and their status  
- **TraceZ** (`/debug/tracez`): Span examination and latency buckets
- **ExpvarZ** (`/debug/expvarz`): Go runtime and component state information

**Configuration**:
```yaml
extensions:
  zpages:
    endpoint: "0.0.0.0:55679"
```

**Usage**:
- Navigate to `http://localhost:55679/debug/` in web browser
- Interactive HTML interface with real-time diagnostic information
- Useful for troubleshooting pipeline issues and component health

## Monitoring Strategy

### Production Monitoring Stack

1. **Health Check** (Port 13133)
   - Use for container orchestration health probes
   - Simple binary health status (healthy/unhealthy)
   - Lightweight endpoint for frequent polling

2. **Prometheus Metrics** (Port 8888)
   - Scrape with Prometheus or compatible monitoring system
   - Track collector performance over time
   - Set up alerts on metric processing failures or resource usage

3. **zPages Diagnostics** (Port 55679)
   - Use for debugging and troubleshooting
   - Real-time insight into collector internals
   - Not typically exposed in production (use for development/debugging)

### Key Metrics to Monitor

**Performance Metrics**:
- `otelcol_exporter_sent_metric_points_total`: Track successful data export
- `otelcol_exporter_send_failed_metric_points_total`: Monitor export failures
- `otelcol_receiver_accepted_metric_points_total`: Verify data ingestion

**Resource Metrics**:
- `otelcol_process_cpu_seconds_total`: Monitor CPU usage trends
- `otelcol_process_memory_rss_bytes`: Track memory consumption
- `otelcol_process_runtime_heap_alloc_bytes`: Go heap allocation

**Pipeline Health**:
- Export success/failure ratios
- Processing latency metrics
- Queue depths and throughput rates

## Container Integration

### Docker Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:13133/health || exit 1
```

### Kubernetes Probes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 13133
  initialDelaySeconds: 30
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health  
    port: 13133
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Docker Compose Health Check
```yaml
services:
  collector:
    # ... other configuration
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:13133/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

## Security Considerations

### Port Exposure
- **Port 13133** (Health): Safe to expose, provides minimal information
- **Port 8888** (Metrics): Contains performance data, consider access controls
- **Port 55679** (zPages): Exposes internal details, restrict access in production

### Network Security
```yaml
# Restrict zPages to localhost in production
extensions:
  zpages:
    endpoint: "127.0.0.1:55679"  # Only local access

# Health check can be exposed widely
extensions:
  health_check:
    endpoint: "0.0.0.0:13133"   # Allow external access
```

## Troubleshooting

### Health Check Issues
```bash
# Check if health endpoint is responding
curl -v http://localhost:13133/health

# Verify port is listening
docker port <container_name> 13133

# Check collector logs for extension errors
docker logs <container_name> | grep -i health
```

### Metrics Issues
```bash
# Test metrics endpoint
curl -v http://localhost:8888/metrics

# Check if Prometheus configuration is correct
docker logs <container_name> | grep -i telemetry

# Verify metrics are being generated
curl -s http://localhost:8888/metrics | grep -c "^# HELP"
```

### zPages Issues
```bash
# Test zPages main page
curl -I http://localhost:55679/debug/

# Check if zPages extension is loaded
curl -s http://localhost:55679/debug/extensionz | grep -i zpages

# Verify no conflicting telemetry settings
# (zPages incompatible with traces level set to 'none')
```

## Best Practices

1. **Always enable health checks** in production deployments
2. **Monitor internal metrics** to track collector performance
3. **Use zPages for debugging** but restrict access in production
4. **Set up alerts** on key performance and error metrics
5. **Regular health monitoring** integrated with orchestration platform
6. **Document monitoring endpoints** for operational teams
7. **Test health checks** in development and staging environments

This comprehensive monitoring setup provides full observability into both the collector's health and performance, enabling proactive monitoring and troubleshooting.