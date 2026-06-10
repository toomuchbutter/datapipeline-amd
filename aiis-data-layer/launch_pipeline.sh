#!/bin/bash

# ==============================================================================
# AegisScale AI - Member 1 Data Infrastructure Automation Launch Script
# Deploys the Live Telemetry Pipeline Engine and FastAPI Gateway in Parallel.
# ==============================================================================

# Ensure execution paths and target processed directories exist
mkdir -p data/processed/prometheus
mkdir -p logs

LOG_PIPELINE="logs/data_pipeline.log"
LOG_API="logs/api_server.log"

echo "======================================================================"
echo "🛡️  AegisScale AI: Launching Member 1 Data Infrastructure Core"
echo "======================================================================"

# Safety function to clean up background processes on script exit (Ctrl+C)
cleanup() {
    echo ""
    echo "🛑 Inbound exit signal caught. Initializing infrastructure teardown..."
    
    if [ -n "$PID_PIPELINE" ]; then
        echo "Killing Data Pipeline Engine (PID: $PID_PIPELINE)..."
        kill $PID_PIPELINE 2>/dev/null
    fi
    
    if [ -n "$PID_API" ]; then
        echo "Killing FastAPI Gateway Server (PID: $PID_API)..."
        kill $PID_API 2>/dev/null
    fi
    
    echo "✅ Teardown complete. All background slots cleared safely."
    exit 0
}

# Bind the cleanup function to the SIGINT interrupt signal (Ctrl+C)
trap cleanup SIGINT

# 1. Start the Live Telemetry Processing and Feature Engineering Factory
echo "⏳ [1/2] Spinning up Continuous Telemetry Polishing Engine..."
python run_live_test.py > "$LOG_PIPELINE" 2>&1 &
PID_PIPELINE=$!
echo "🟢 Telemetry Engine running in background slot (PID: $PID_PIPELINE)"
echo "   ↳ Logs being compiled to: $LOG_PIPELINE"

# Small delay to let the engine write its initial Parquet matrix file before API reads it
sleep 2

# 2. Launch the FastAPI REST Gateway Window
echo "⏳ [2/2] Exposing REST API Gateway on Port 8000..."
python api_server.py > "$LOG_API" 2>&1 &
PID_API=$!
echo "🟢 FastAPI Gateway running in background slot (PID: $PID_API)"
echo "   ↳ Logs being compiled to: $LOG_API"

echo "======================================================================"
echo "🚀 SUCCESS: Infrastructure Active & Listening!"
echo "   ↳ API Health URL:  http://localhost:8050/health"
echo "   ↳ Telemetry URL:   http://localhost:8050/api/v1/metrics/latest"
echo "======================================================================"
echo "💡 Press [Ctrl+C] to halt the loop and terminate both services safely."
echo "======================================================================"

# Keep the shell script alive and monitor background job queues
wait $PID_PIPELINE $PID_API
