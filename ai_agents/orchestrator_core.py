import time
import os
import json
import requests
from typing import Generator
from agno.team import Team
from agents_pool import dna_agent, anomaly_agent, capacity_agent, finops_hardware_agent, safety_governor
from shared_config import shared_model

# Construct the hierarchical Orchestrator Team
orchestrator_team = Team(
    name="Workload DNA Orchestrator Core",
    model=shared_model,
    members=[
        dna_agent, 
        anomaly_agent, 
        capacity_agent, 
        finops_hardware_agent, 
        safety_governor
    ],
    instructions=[
        "You are the Core Coordinator. Manage information transfer among workers.",
        "1. Direct the Workload DNA Profiler to footprint the system.",
        "2. Direct the Anomaly Intelligence Inspector to scan for operational leaks.",
        "3. Have the Capacity Planner extract sizing requirements.",
        "4. Have the FinOps & AMD Hardware Critic evaluate allocations and apply AMD_INSTINCT_GPU / AMD_EPYC_CPU routing rules.",
        "5. Pass the final matrix to the Safety Governor for digital twin clearance calculation.",
        "Synthesize all outputs into a structural, condensed system report. Omit conversational conversational filler."
    ],
    markdown=True
)

def initialize_shared_cache():
    """Ensures a valid JSON state framework exists on the virtual machine disk."""
    if not os.path.exists("system_state.json"):
        blank = {
            "system_health": "HEALTHY", 
            "active_nodes": 4, 
            "incident_history": [], 
            "postmortems": [],
            "cpu_history": [87.92],
            "node_history": [3],
            "timestamps": [time.strftime("%H:%M:%S")],
            "current_telemetry": {"cpu_avg": 87.92, "memory_avg": 205.38, "timestamp": time.strftime("%H:%M:%S")},
            "dna_profile": {"type": "BURST"},
            "anomaly_report": {"anomaly_detected": False},
            "capacity_plan": {"recommended_pods": 3},
            "hardware_finops": {"hardware_selection": "AMD_INSTINCT_GPU/RIIS_2100"},
            "safety_clearance": {"clearance": False, "digital_twin_simulated_risk": "HIGH"}
        }
        with open("system_state.json", "w") as f:
            json.dump(blank, f, indent=2)

def stream_boardroom_audit(prompt: str) -> Generator[str, None, None]:
    """
    Agno Streaming Engine: Pulls live metrics from port 8050, drives the 
    team loop, intercepts chunked tokens, and updates system state mid-stream.
    """
    initialize_shared_cache()
    
    # Update local telemetry cache directly from port 8050 before the streaming run
    try:
        r = requests.get("http://localhost:8050/api/v1/metrics/latest", timeout=2)
        if r.status_code == 200:
            with open("system_state.json", "r") as f:
                state = json.load(f)
            metrics = r.json()
            state["current_telemetry"] = metrics
            state["cpu_history"].append(float(metrics.get("cpu_avg", 87.92)))
            state["node_history"].append(int(state.get("active_nodes", 3)))
            state["timestamps"].append(time.strftime("%H:%M:%S"))
            
            state["cpu_history"] = state["cpu_history"][-30:]
            state["node_history"] = state["node_history"][-30:]
            state["timestamps"] = state["timestamps"][-30:]
            with open("system_state.json", "w") as f:
                json.dump(state, f, indent=2)
    except:
        pass

    # FIXED: Swapped .stream() out for the correct native .run() iterator mechanism
    event_stream = orchestrator_team.run(prompt, stream=True, stream_events=True)
    
    for event in event_stream:
        # Extract framework metadata safely
        event_type = getattr(event, "event", None)
        content = getattr(event, "content", None)
        
        # Fallback edge handler: if Agno passes raw strings directly
        if not event_type and isinstance(event, str):
            yield event
            continue
            
        # Mid-Stream Lifecycle Hook: Intercept intermediate tool calls to flag the frontend UI
        if event_type and ("Tool" in str(event_type) or "tool" in str(event_type)) and "Started" in str(event_type):
            try:
                with open("system_state.json", "r") as f:
                    st_data = json.load(f)
                st_data["system_health"] = "SCALING_ACTIVE"
                with open("system_state.json", "w") as f:
                    json.dump(st_data, f, indent=2)
            except:
                pass
                
        # Filter for token chunks containing printable content responses
        if event_type and ("Content" in str(event_type) or "content" in str(event_type)) and content:
            yield content

if __name__ == "__main__":
    print("⏳ Running engine standalone pipeline text verification stream...")
    for token in stream_boardroom_audit("Initiate comprehensive live telemetry evaluation sequence for current port 8050 systems."):
        print(token, end="", flush=True)
    print("\n\n✅ Stream test completed successfully.")
