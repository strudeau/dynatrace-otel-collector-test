#!/usr/bin/env python3
"""
Dynatrace OpenTelemetry Collector Diagnostics Script
Cross-platform diagnostic tool for monitoring collector health and OTLP HTTP exporter status.

Usage:
    python diagnostics.py                    # Run all diagnostics
    python diagnostics.py --health          # Health check only
    python diagnostics.py --metrics         # Metrics analysis only
    python diagnostics.py --export-stats    # Export statistics only
    python diagnostics.py --continuous      # Continuous monitoring
"""

import sys
import time
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

class CollectorDiagnostics:
    def __init__(self, host: str = "localhost"):
        self.host = host
        self.health_url = f"http://{host}:13133/health"
        self.metrics_url = f"http://{host}:8888/metrics"
        self.zpages_url = f"http://{host}:55679/debug/"
        
    def print_banner(self):
        """Print diagnostic banner with timestamp"""
        print("=" * 70)
        print("🔍 DYNATRACE OTEL COLLECTOR DIAGNOSTICS")
        print("=" * 70)
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  Host: {self.host}")
        print("=" * 70)

    def check_health(self) -> Tuple[bool, str]:
        """Check collector health status"""
        try:
            with urlopen(self.health_url, timeout=10) as response:
                status = response.read().decode('utf-8')
                return True, status.strip()
        except (URLError, HTTPError) as e:
            return False, f"Health check failed: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def get_metrics(self) -> Tuple[bool, str]:
        """Fetch Prometheus metrics"""
        try:
            with urlopen(self.metrics_url, timeout=10) as response:
                metrics = response.read().decode('utf-8')
                return True, metrics
        except (URLError, HTTPError) as e:
            return False, f"Metrics fetch failed: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def parse_metric_value(self, metrics_text: str, metric_name: str, labels: str = "") -> Optional[float]:
        """Extract metric value from Prometheus format text"""
        lines = metrics_text.split('\n')
        
        for line in lines:
            if line.startswith(metric_name):
                # Check if this line contains the required labels (if any)
                if labels and labels not in line:
                    continue
                try:
                    # Extract value (last part after space)
                    value_str = line.split()[-1]
                    return float(value_str)
                except (ValueError, IndexError):
                    continue
        return None

    def analyze_export_metrics(self, metrics_text: str) -> Dict[str, any]:
        """Analyze OTLP HTTP exporter metrics"""
        analysis = {
            'otlphttp_sent_metrics': 0,
            'otlphttp_failed_metrics': 0,
            'otlphttp_queue_size': 0,
            'otlphttp_queue_capacity': 0,
            'total_received_metrics': 0,
            'success_rate': 0.0,
            'queue_utilization': 0.0
        }

        # Extract OTLP HTTP exporter specific metrics (try both metric name formats)
        analysis['otlphttp_sent_metrics'] = (
            self.parse_metric_value(metrics_text, 'otelcol_exporter_sent_metric_points__datapoints__total', 'exporter="otlphttp"') or
            self.parse_metric_value(metrics_text, 'otelcol_exporter_sent_metric_points_total', 'exporter="otlphttp"') or 0
        )

        analysis['otlphttp_failed_metrics'] = (
            self.parse_metric_value(metrics_text, 'otelcol_exporter_send_failed_metric_points__datapoints__total', 'exporter="otlphttp"') or
            self.parse_metric_value(metrics_text, 'otelcol_exporter_send_failed_metric_points_total', 'exporter="otlphttp"') or 0
        )

        analysis['otlphttp_queue_size'] = (
            self.parse_metric_value(metrics_text, 'otelcol_exporter_queue_size__batches_', 'exporter="otlphttp"') or
            self.parse_metric_value(metrics_text, 'otelcol_exporter_queue_size', 'exporter="otlphttp"') or 0
        )

        analysis['otlphttp_queue_capacity'] = (
            self.parse_metric_value(metrics_text, 'otelcol_exporter_queue_capacity__batches_', 'exporter="otlphttp"') or
            self.parse_metric_value(metrics_text, 'otelcol_exporter_queue_capacity', 'exporter="otlphttp"') or 0
        )

        # Total metrics received by collector (try both formats)
        analysis['total_received_metrics'] = (
            self.parse_metric_value(metrics_text, 'otelcol_receiver_accepted_metric_points__datapoints__total') or
            self.parse_metric_value(metrics_text, 'otelcol_receiver_accepted_metric_points_total') or 0
        )

        # Calculate success rate
        total_attempts = analysis['otlphttp_sent_metrics'] + analysis['otlphttp_failed_metrics']
        if total_attempts > 0:
            analysis['success_rate'] = (analysis['otlphttp_sent_metrics'] / total_attempts) * 100

        # Calculate queue utilization
        if analysis['otlphttp_queue_capacity'] > 0:
            analysis['queue_utilization'] = (analysis['otlphttp_queue_size'] / analysis['otlphttp_queue_capacity']) * 100

        return analysis

    def print_health_status(self):
        """Print health check results"""
        print("\n🏥 HEALTH CHECK")
        print("-" * 50)
        
        is_healthy, status_message = self.check_health()
        
        if is_healthy:
            print(f"✅ Status: {status_message}")
            print("🔗 Health Endpoint: http://localhost:13133/health")
        else:
            print(f"❌ Status: {status_message}")
            print("💡 Troubleshooting:")
            print("   - Ensure collector container is running")
            print("   - Verify port 13133 is exposed")
            print("   - Check docker-compose logs for errors")

    def print_export_statistics(self):
        """Print OTLP HTTP exporter statistics"""
        print("\n📊 OTLP HTTP EXPORTER STATISTICS")
        print("-" * 50)
        
        metrics_success, metrics_data = self.get_metrics()
        
        if not metrics_success:
            print(f"❌ Unable to fetch metrics: {metrics_data}")
            print("💡 Troubleshooting:")
            print("   - Ensure collector container is running")
            print("   - Verify port 8888 is exposed")
            print("   - Check internal telemetry configuration")
            return

        analysis = self.analyze_export_metrics(metrics_data)
        
        # Export Success/Failure
        print(f"📤 Metrics Sent to Dynatrace: {int(analysis['otlphttp_sent_metrics']):,}")
        print(f"❌ Failed Export Attempts: {int(analysis['otlphttp_failed_metrics']):,}")
        print(f"📈 Success Rate: {analysis['success_rate']:.1f}%")
        
        # Queue Status  
        print(f"📋 Export Queue Size: {int(analysis['otlphttp_queue_size']):,}")
        print(f"📦 Queue Capacity: {int(analysis['otlphttp_queue_capacity']):,}")
        print(f"⚡ Queue Utilization: {analysis['queue_utilization']:.1f}%")
        
        # Overall Pipeline Health
        print(f"🔄 Total Metrics Received: {int(analysis['total_received_metrics']):,}")
        
        # Status Assessment
        self.print_status_assessment(analysis)

    def print_status_assessment(self, analysis: Dict[str, any]):
        """Print overall status assessment and recommendations"""
        print(f"\n🎯 STATUS ASSESSMENT")
        print("-" * 50)
        
        # Success rate assessment
        success_rate = analysis['success_rate']
        if success_rate >= 95:
            print("✅ Export Health: EXCELLENT")
        elif success_rate >= 80:
            print("⚠️  Export Health: GOOD (monitor for improvements)")
        elif success_rate >= 50:
            print("🟡 Export Health: DEGRADED (investigate failures)")
        else:
            print("🔴 Export Health: CRITICAL (immediate attention required)")

        # Queue utilization assessment
        queue_util = analysis['queue_utilization']
        if queue_util < 50:
            print("✅ Queue Status: HEALTHY")
        elif queue_util < 80:
            print("⚠️  Queue Status: MODERATE (monitor load)")
        else:
            print("🔴 Queue Status: HIGH (risk of data loss)")

        # Recommendations
        if analysis['otlphttp_failed_metrics'] > 0:
            print("\n💡 RECOMMENDATIONS:")
            print("   - Check Dynatrace API token permissions")
            print("   - Verify DT_ENDPOINT configuration")
            print("   - Review network connectivity to Dynatrace")
            print("   - Check collector logs: docker-compose logs collector")

        if queue_util > 70:
            print("\n💡 QUEUE RECOMMENDATIONS:")
            print("   - Consider increasing queue_size in configuration")
            print("   - Add more num_consumers for parallel processing")
            print("   - Review batch processor settings")

    def print_monitoring_endpoints(self):
        """Print available monitoring endpoints"""
        print("\n🔗 MONITORING ENDPOINTS")
        print("-" * 50)
        print(f"🏥 Health Check: http://localhost:13133/health")
        print(f"📊 Metrics (Prometheus): http://localhost:8888/metrics")
        print(f"🔍 zPages Web UI: http://localhost:55679/debug/")
        print(f"   • ServiceZ: http://localhost:55679/debug/servicez")
        print(f"   • PipelineZ: http://localhost:55679/debug/pipelinez")
        print(f"   • ExtensionZ: http://localhost:55679/debug/extensionz")

    def run_diagnostics(self, health_only=False, metrics_only=False, export_stats_only=False):
        """Run comprehensive diagnostics"""
        self.print_banner()
        
        if health_only or not (metrics_only or export_stats_only):
            self.print_health_status()
            
        if metrics_only or export_stats_only or not (health_only):
            self.print_export_statistics()
            
        if not (health_only or metrics_only or export_stats_only):
            self.print_monitoring_endpoints()

    def continuous_monitoring(self, interval: int = 30):
        """Run continuous monitoring with specified interval"""
        print(f"🔄 Starting continuous monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                self.run_diagnostics()
                print(f"\n⏰ Sleeping for {interval} seconds...")
                print("=" * 70)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")

def main():
    parser = argparse.ArgumentParser(description='Dynatrace OTel Collector Diagnostics')
    parser.add_argument('--host', default='localhost', help='Collector host (default: localhost)')
    parser.add_argument('--health', action='store_true', help='Health check only')
    parser.add_argument('--metrics', action='store_true', help='Metrics analysis only')  
    parser.add_argument('--export-stats', action='store_true', help='Export statistics only')
    parser.add_argument('--continuous', action='store_true', help='Continuous monitoring')
    parser.add_argument('--interval', type=int, default=30, help='Monitoring interval in seconds (default: 30)')
    
    args = parser.parse_args()
    
    diagnostics = CollectorDiagnostics(args.host)
    
    if args.continuous:
        diagnostics.continuous_monitoring(args.interval)
    else:
        diagnostics.run_diagnostics(
            health_only=args.health,
            metrics_only=args.metrics,
            export_stats_only=args.export_stats
        )

if __name__ == "__main__":
    main()