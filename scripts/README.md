# Diagnostics Scripts

This directory contains cross-platform diagnostic tools for monitoring your Dynatrace OpenTelemetry Collector.

## 🔍 Available Diagnostics

### 1. **Python Script (Cross-Platform)**
- **File**: `diagnostics.py` 
- **Supports**: Windows, Linux, macOS
- **Requirements**: Python 3.7+

### 2. **Windows Batch Script**
- **File**: `run-diagnostics.bat`
- **Double-click to run or execute in Command Prompt**

### 3. **Linux/macOS Shell Script**  
- **File**: `run-diagnostics.sh`
- **Execute with**: `./run-diagnostics.sh`

### 4. **Docker Container**
- **Continuous monitoring in containerized environment**
- **No local Python installation required**

## 🚀 Quick Start

### **Windows Users:**
```powershell
# Option 1: Double-click run-diagnostics.bat

# Option 2: PowerShell
cd scripts
python diagnostics.py

# Option 3: Command Prompt  
cd scripts
run-diagnostics.bat
```

### **Linux/macOS Users:**
```bash
# Option 1: Shell script
cd scripts
./run-diagnostics.sh

# Option 2: Direct Python
cd scripts  
python3 diagnostics.py
```

### **Docker Diagnostics Container:**
```bash
# Run diagnostics in Docker (no local Python needed)
cd scripts
docker-compose -f docker-compose.diagnostics.yml up --build

# One-time diagnostic check
docker build -f Dockerfile.diagnostics -t otel-diagnostics .
docker run --rm --network host otel-diagnostics
```

## 📊 Diagnostic Options

### **Basic Usage:**
```bash
python diagnostics.py                    # Full diagnostic report
python diagnostics.py --health          # Health check only  
python diagnostics.py --export-stats    # Export statistics only
python diagnostics.py --continuous      # Continuous monitoring
```

### **Advanced Options:**
```bash
python diagnostics.py --host collector-host  # Remote collector
python diagnostics.py --interval 60          # Custom monitoring interval
```

## 📈 What Gets Monitored

### **Health Status**
- ✅ Collector overall health
- 🔗 Health endpoint accessibility  
- ⚡ Response time validation

### **OTLP HTTP Exporter Statistics**
- 📤 **Metrics Sent**: Successfully exported to Dynatrace
- ❌ **Failed Exports**: Failed attempts with error analysis
- 📈 **Success Rate**: Export success percentage
- 📋 **Queue Status**: Export queue size and utilization
- 🔄 **Pipeline Health**: End-to-end metrics flow

### **Performance Metrics**
- ⚡ Queue utilization percentage
- 📦 Queue capacity vs. current load
- 🎯 Real-time success/failure rates

## 🎯 Status Indicators

| Status | Description | Action |
|--------|-------------|---------|
| ✅ **EXCELLENT** | 95%+ success rate | Continue monitoring |
| ⚠️ **GOOD** | 80-95% success rate | Monitor for improvements |
| 🟡 **DEGRADED** | 50-80% success rate | Investigate failures |
| 🔴 **CRITICAL** | <50% success rate | Immediate attention required |

## 🔗 Monitoring Endpoints

The diagnostics tools check these collector endpoints:

| Endpoint | Port | Purpose |
|----------|------|---------|
| `/health` | 13133 | Health status check |
| `/metrics` | 8888 | Prometheus metrics |
| `/debug/` | 55679 | zPages web interface |

## 🛠️ Troubleshooting

### **"Connection Refused" Errors**
```bash
# Ensure collector is running
docker-compose up -d

# Check container status
docker-compose ps

# View collector logs
docker-compose logs collector
```

### **"No metrics found" Errors**  
```bash
# Verify internal telemetry is enabled
# Check config/collector-config.yaml:
#   telemetry:
#     metrics:
#       level: detailed
```

### **Python Not Found (Windows)**
1. Install Python from https://python.org
2. Add Python to system PATH
3. Restart Command Prompt/PowerShell

### **Permission Errors (Linux/macOS)**
```bash
# Make script executable
chmod +x run-diagnostics.sh

# Install Python if needed (Ubuntu/Debian)
sudo apt update && sudo apt install python3
```

## 🐳 Docker Diagnostics

### **Standalone Diagnostics Container:**
```bash
# Build diagnostics image
docker build -f Dockerfile.diagnostics -t otel-diagnostics .

# Run one-time diagnostics
docker run --rm --network host otel-diagnostics

# Run continuous monitoring
docker run --rm --network host otel-diagnostics --continuous --interval 30
```

### **Full Stack with Diagnostics:**
```bash
# Run collector + diagnostics together
docker-compose -f docker-compose.diagnostics.yml up --build

# View diagnostics logs
docker-compose -f docker-compose.diagnostics.yml logs diagnostics
```

This provides complete diagnostic coverage for your Dynatrace OpenTelemetry Collector deployment across all platforms!