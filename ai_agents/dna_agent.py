import json
import requests
from agno.agent import Agent
from agno.models.vllm import VLLM

def fetch_live_telemetry_from_bridge() -> str:
    """Queries the running aiis-data-layer on port 8050 for fresh metrics."""
    try:
        r = requests.get("http://localhost:8050/api/v1/metrics/latest", timeout=3)
        if r.status_code == 200:
            return json.dumps(r.json())
        return json.dumps({"error": f"API port error: {r.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Failed connection to data layer: {str(e)}"})

dna_agent = Agent(
    name="Workload DNA Agent",
    model=VLLM(id="Qwen3-4B", base_url="http://localhost:8000/v1", api_key="abc-123"),
    instructions=[
        "You are the Workload DNA Profiler.",
        "Analyze the incoming live telemetry from port 8050 and compute an operational fingerprint.",
        "Evaluate patterns like CPU growth and request rates.",
        "Your output MUST be a strict JSON object with no markdown text, matching this layout:",
        '{"type": "FLASH_SALE_SURGE" or "PERIODIC_NORMAL", "seasonality": float, "burstiness": float, "predictability": float, "confidence": float}'
    ],
    tools=[fetch_live_telemetry_from_bridge]
)

def run_dna_profiling():
    response = dna_agent.run("Analyze active telemetry data from port 8050 and generate a DNA fingerprint profile.")
    try:
        profile = json.loads(response.content.strip())
        with open("system_state.json", "r") as f:
            state = json.load(f)
        state["dna_profile"] = profile
        with open("system_state.json", "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        pass
