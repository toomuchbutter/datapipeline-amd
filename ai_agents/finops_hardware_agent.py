import json
import requests
from agno.agent import Agent
from agno.models.vllm import VLLM

def fetch_plan_for_hardware_critique() -> str:
    try:
        r = requests.get("http://localhost:8050/api/v1/metrics/latest", timeout=3).json()
        with open("system_state.json", "r") as f:
            state = json.load(f)
        return json.dumps({"telemetry": r, "proposed_plan": state.get("capacity_plan", {})})
    except:
        return json.dumps({})

finops_hardware_agent = Agent(
    name="FinOps Hardware Optimizer Agent",
    model=VLLM(id="Qwen3-4B", base_url="http://localhost:8000/v1", api_key="abc-123"),
    instructions=[
        "You are the FinOps & AMD Hardware Critic.",
        "Evaluate the proposed capacity allocations against corporate budgets and apply hardware routing rules:",
        "- Route high-load, bursty traffic or scaling anomalies to 'AMD_INSTINCT_GPU' server pools.",
        "- Route standard, steady transactional code to 'AMD_EPYC_CPU' pools to maximize performance-per-watt metrics.",
        "Your output MUST be a strict JSON object with no markdown text, matching this layout:",
        '{"approved": bool, "optimized_nodes": int, "hardware_selection": "AMD_EPYC_CPU" or "AMD_INSTINCT_GPU", "efficiency_justification": "string", "critic_confidence": float}'
    ],
    tools=[fetch_plan_for_hardware_critique]
)

def run_hardware_finops_critique():
    response = finops_hardware_agent.run("Evaluate the actor's capacity plan against our AMD hardware efficiency matrix.")
    try:
        report = json.loads(response.content.strip())
        with open("system_state.json", "r") as f:
            state = json.load(f)
        state["hardware_finops"] = report
        with open("system_state.json", "w") as f:
            json.dump(state, f, indent=2)
    except:
        pass
