# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project creates a simple test environment for the Dynatrace OpenTelemetry Collector using Docker. The goal is to demonstrate host metrics collection using the hostmetrics receiver and output validation using the debug exporter.

## Project Goals

- Set up Dynatrace OpenTelemetry Collector in a Docker container
- Configure hostmetrics receiver to collect system metrics
- Use debug exporter for testing and validation (not Dynatrace otlphttp exporter initially)
- Create a reproducible testing environment

## Key Components

- **Dynatrace OpenTelemetry Collector**: Custom distribution with Dynatrace-specific capabilities
- **Host Metrics Receiver**: Collects system metrics (CPU, memory, disk, network)
- **Debug Exporter**: Outputs metrics to console for testing and validation
- **Docker Setup**: Containerized environment for easy deployment and testing

## Reference Documentation

1. [Dynatrace OpenTelemetry Collector Docs](https://docs.dynatrace.com/docs/ingest-from/opentelemetry/collector)
2. [Dynatrace OTel Collector GitHub](https://github.com/Dynatrace/dynatrace-otel-collector)
3. [Configuration Examples](https://github.com/Dynatrace/dynatrace-otel-collector/tree/main/config_examples)
4. [Host Metrics Example](https://github.com/Dynatrace/dynatrace-otel-collector/blob/main/config_examples/host-metrics.yaml)
5. [Debug Exporter Documentation](https://github.com/open-telemetry/opentelemetry-collector/blob/main/exporter/debugexporter/README.md)

## Development Commands

```bash
# Build and run the collector
docker-compose up --build

# View logs to see debug output
docker-compose logs -f collector

# Stop the setup
docker-compose down
```

## Testing Approach

1. Start with hostmetrics receiver + debug exporter configuration
2. Validate metrics collection through debug output
3. Only after successful testing, consider adding Dynatrace otlphttp exporter