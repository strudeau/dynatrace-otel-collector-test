# Dynatrace OpenTelemetry Collector Docker Test

This project demonstrates a simple test setup for the Dynatrace OpenTelemetry Collector using Docker, configured to collect host metrics and output them using the debug exporter.

## Components

- **Dynatrace OpenTelemetry Collector**: Official Dynatrace distribution
- **Host Metrics Receiver**: Collects system metrics (CPU, memory, disk, network, processes)
- **Debug Exporter**: Outputs collected metrics to console for testing

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

## Configuration

The collector is configured via `collector-config.yaml` with:

- **Receivers**: hostmetrics collecting every 10 seconds
- **Processors**: resource detection, cumulative to delta conversion, batching
- **Exporters**: debug exporter with detailed verbosity

## Testing

The debug exporter will output detailed metrics information to the console, allowing you to verify that host metrics are being collected properly. Look for:

- CPU utilization metrics
- Memory usage and limits
- Disk filesystem utilization
- Network statistics
- Process counts and utilization

## Next Steps

Once host metrics collection is verified working with the debug exporter, you can:

1. Replace the debug exporter with the Dynatrace otlphttp exporter
2. Add environment variables for `DT_ENDPOINT` and `API_TOKEN`
3. Configure additional receivers or processors as needed

## Troubleshooting

- Ensure Docker has sufficient permissions to access host metrics
- Check container logs for any permission or configuration errors
- Verify that the collector container has access to `/proc`, `/sys`, and `/etc` from the host