import json
import requests
from agno.agent import Agent
from agno.models.vllm import VLLM

def fetch_aggregated_state_for_capacity() -> str:
    try:
        r = requests.get("http://localhost:8050/api/v1/metrics/latest", timeout=3).json()
        with open("system_state.json", "r") as f:
            dna = json.load(f).get("dna_profile", {})
        return json.dumps({"telemetry": r, "dna_profile": dna})
    except:
        return json.dumps({})

capacity_agent = Agent(
    name="Capacity Planner Agent",
    model=VLLM(id="Qwen3-4B", base_url="http://localhost:8000/v1", api_key="abc-123"),
    instructions=[
        "You are the Capacity Planner (The Actor Engine).",
        "Review the live telemetry and DNA profiles to calculate multivariate resource demand targets.",
        "Your output MUST be a strict JSON object with no markdown text, matching this layout:",
        '{"recommended_pods": int, "recommended_nodes": int, "predicted_latency_ms": int, "confidence": float}'
    ],
    tools=[fetch_aggregated_state_for_capacity]
)

def run_capacity_planning():
    response = capacity_agent.run("Formulate our proactive 15-minute resource requirement blueprint.")
    try:
        plan = json.loads(response.content.strip())
        with open("system_state.json", "r") as f:
            state = json.load(f)
        state["capacity_plan"] = plan
        with open("system_state.json", "w") as f:
            json.dump(state, f, indent=2)
    except:
        pass
