import json
import requests
from agno.agent import Agent
from agno.models.vllm import VLLM

def fetch_live_telemetry_for_anomaly() -> str:
    try:
        r = requests.get("http://localhost:8050/api/v1/metrics/latest", timeout=3)
        return json.dumps(r.json()) if r.status_code == 200 else json.dumps({})
    except:
        return json.dumps({})

anomaly_agent = Agent(
    name="Anomaly Intelligence Agent",
    model=VLLM(id="Qwen3-4B", base_url="http://localhost:8000/v1", api_key="abc-123"),
    instructions=[
        "You are the Anomaly Intelligence Inspector.",
        "Scan the live port 8050 metrics data for resource degradation flags or memory leaks.",
        "Your output MUST be a strict JSON object with no markdown text, matching this layout:",
        '{"anomaly_detected": bool, "classification": "MEMORY_LEAK" or "NONE", "confidence_score": float, "root_signal": "string"}'
    ],
    tools=[fetch_live_telemetry_for_anomaly]
)

def run_anomaly_check():
    response = anomaly_agent.run("Evaluate active cluster metrics for running anomaly system indicators.")
    try:
        report = json.loads(response.content.strip())
        with open("system_state.json", "r") as f:
            state = json.load(f)
        state["anomaly_report"] = report
        with open("system_state.json", "w") as f:
            json.dump(state, f, indent=2)
    except:
        pass
