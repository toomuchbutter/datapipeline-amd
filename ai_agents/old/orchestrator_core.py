import time
import os
import json
import requests

from dna_agent import run_dna_profiling
from anomaly_agent import run_anomaly_check
from capacity_agent import run_capacity_planning
from finops_hardware_agent import run_hardware_finops_critique
from safety_governor import run_safety_clearance

def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("=" * 80)
    print("🛡️   AEGISSCALE AI: AUTONOMOUS INFRASTRUCTURE INTELLIGENCE ENGINE")
    print("    [ Standalone CLI Boardroom & Digital Twin Control Loop ]")
    print("=" * 80)
    print("📡 Inbound Data Stream Portal: http://localhost:8050/api/v1/metrics/latest")
    print("🧠 Model Inference Vector:    http://localhost:8000/v1 (Qwen3-4B)")
    print("=" * 80)

def initialize_shared_cache():
    """Builds a fresh dashboard tracking cache if missing."""
    if not os.path.exists("system_state.json"):
        blank = {"system_health": "HEALTHY", "active_nodes": 4, "incident_history": [], "postmortems": []}
        with open("system_state.json", "w") as f:
            json.dump(blank, f, indent=2)

def start_terminal_loop():
    initialize_shared_cache()
    print_banner()
    print("🚀 Standalone Terminal Engine online. Monitoring stream. Press Ctrl+C to halt.")
    time.sleep(2)
    
    cycle = 0
    try:
        while True:
            cycle += 1
            # Fetch current live data layer metrics directly from port 8050
            try:
                metrics_response = requests.get("http://localhost:8050/api/v1/metrics/latest", timeout=2)
                if metrics_response.status_code != 200:
                    print("\n⏳ [Awaiting Data] Data gateway on port 8050 active but returned empty payload...")
                    time.sleep(5)
                    continue
                metrics = metrics_response.json()
            except Exception:
                print("\n🔌 [Connection Error] Port 8050 data layer offline. Ensure your pipeline is active.")
                time.sleep(5)
                continue
                
            # Synchronize local cache with incoming data stream values
            with open("system_state.json", "r") as f:
                state = json.load(f)
            state["current_telemetry"] = metrics
            with open("system_state.json", "w") as f:
                json.dump(state, f, indent=2)

            print("\n" + "⚡" * 40)
            print(f" AGENT BOARDROOM CYCLE #{cycle} | Live Data Timestamp: {metrics.get('timestamp')}")
            print("⚡" * 40)
            print(f"📊 Live Vitals -> CPU: {metrics.get('cpu_avg'):.1f}% | Mem: {metrics.get('memory_avg'):.1f}% | Nodes: {state.get('active_nodes')}")
            print("-" * 80)
            
            # Run sequential boardroom reasoning tracks
            print("⏳ [Stage 1/5] Extracting Workload DNA Fingerprint...")
            run_dna_profiling()
            with open("system_state.json", "r") as f: state = json.load(f)
            print(f"   ↳ 🧬 DNA Profile: Archetype -> {state.get('dna_profile', {}).get('type', 'UNKNOWN')}")
            print("-" * 80)
            time.sleep(1)
            
            print("⏳ [Stage 2/5] Inspecting Telemetry for Infrastructure Anomalies...")
            run_anomaly_check()
            with open("system_state.json", "r") as f: state = json.load(f)
            print(f"   ↳ ⚠️  Anomaly Scan Result: Flagged -> {state.get('anomaly_report', {}).get('anomaly_detected')}")
            print("-" * 80)
            time.sleep(1)
            
            print("⏳ [Stage 3/5] Projecting Multivariate Resource Requirements (Actor)...")
            run_capacity_planning()
            with open("system_state.json", "r") as f: state = json.load(f)
            print(f"   ↳ 🔮 Proposed Fleet Scale: Target Pods -> {state.get('capacity_plan', {}).get('recommended_pods')}")
            print("-" * 80)
            time.sleep(1)
            
            print("⏳ [Stage 4/5] Executing FinOps Budget Gates & AMD Core Routing (Critic)...")
            run_hardware_finops_critique()
            with open("system_state.json", "r") as f: state = json.load(f)
            print(f"   ↳ 🏎️  Hardware Route Selection: Allocated -> {state.get('hardware_finops', {}).get('hardware_selection')}")
            print("-" * 80)
            time.sleep(1)
            
            print("⏳ [Stage 5/5] Running Digital Twin Simulations & Issuing Safety Clearance...")
            run_safety_clearance()
            with open("system_state.json", "r") as f: state = json.load(f)
            print(f"   ↳ 🛡️  Safety Verdict: Risk Profile -> {state.get('safety_clearance', {}).get('digital_twin_simulated_risk')}")
            print(f"   ↳ 📈 Fleet Capacity Settled: Active Cluster Nodes -> {state.get('active_nodes')}")
            
            print("\n" + "=" * 80)
            print(f"💤 Cycle #{cycle} complete. Re-evaluating data stream in 12 seconds...")
            print("=" * 80)
            time.sleep(12)
            
    except KeyboardInterrupt:
        print("\n🛑 Standalone multi-agent terminal harness halted.")

if __name__ == "__main__":
    start_terminal_loop()
