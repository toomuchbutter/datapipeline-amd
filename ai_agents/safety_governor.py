import json
import time
from agno.agent import Agent
from agno.models.vllm import VLLM

def read_full_state_for_safety() -> str:
    with open("system_state.json", "r") as f:
        return json.dumps(json.load(f))

safety_governor_agent = Agent(
    name="Safety Governor Agent",
    model=VLLM(id="Qwen3-4B", base_url="http://localhost:8000/v1", api_key="abc-123"),
    instructions=[
        "You are the Safety Governor and Autonomous Postmortem Generator.",
        "Review the entire system plan matrix. Run a digital twin safety clearance calculation to verify stability.",
        "Your output MUST be a strict JSON object with no markdown text, matching this layout:",
        '{"clearance": bool, "final_nodes_count": int, "digital_twin_simulated_risk": "LOW" or "HIGH", "postmortem_markdown": "string"}'
    ],
    tools=[read_full_state_for_safety]
)

def run_safety_clearance():
    response = safety_governor_agent.run("Verify safety parameters via digital twin simulations and compile an architectural postmortem.")
    try:
        clearance = json.loads(response.content.strip())
        with open("system_state.json", "r") as f:
            state = json.load(f)
            
        state["safety_clearance"] = clearance
        if clearance["clearance"]:
            old_nodes = state["active_nodes"]
            state["active_nodes"] = clearance["final_nodes_count"]
            
            if old_nodes != clearance["final_nodes_count"]:
                state["incident_history"].append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "event": f"Capacity scaled from {old_nodes} to {clearance['final_nodes_count']} nodes.",
                    "risk_index": clearance["digital_twin_simulated_risk"]
                })
                state["postmortems"].append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "report": clearance["postmortem_markdown"]
                })
        with open("system_state.json", "w") as f:
            json.dump(state, f, indent=2)
    except:
        pass
