import json
import requests
from agno.agent import Agent
from agno.models.vllm import VLLM

# 1. Define the Telemetry Tool function for the Agno Agent
def fetch_latest_cluster_metrics() -> str:
    """
    Queries the Member 1 FastAPI Gateway on Port 8050 to retrieve the absolute newest
    anomaly-filtered infrastructure utilization data, pattern classifications, and carbon metrics.
    """
    url = "http://localhost:8050/api/v1/metrics/latest"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            # Inject the clean JSON payload directly into the LLM's thought stream
            return json.dumps(response.json())
        return json.dumps({"error": f"FastAPI Gateway returned status code {response.status_code}"})
    except requests.exceptions.ConnectionError:
        return json.dumps({"error": "Connection failed. Ensure launch_pipeline.sh is running on port 8050."})
    except Exception as e:
        return json.dumps({"error": f"Unexpected network exception: {str(e)}"})

# 2. Build the System Prompt and Capacity Rule Matrix
capacity_planning_instructions = [
    "You are the Autonomous Digital Infrastructure Manager (AegisScale AI Core).",
    "Your objective is to optimize cloud infrastructure capacity, protect application SLAs, and maximize AMD performance-per-watt efficiency.",
    "Always invoke the 'fetch_latest_cluster_metrics' tool first to examine the system's operational vitals.",
    "",
    "CRITICAL THRESHOLD LOGIC ASSIGNMENTS:",
    "- Look specifically at the 'future_cpu_15m' metric (the ML prediction token).",
    "- If 'future_cpu_15m' > 80.0%: Issue an immediate 'SCALE_UP' action directive to add 2 AMD EPYC nodes to protect revenue and prevent application checkout crashes.",
    "- If 'future_cpu_15m' < 40.0%: Issue a 'SCALE_DOWN' directive to terminate 1 node, eliminating 'zombie' idle compute waste and reclaiming budget capital.",
    "- Otherwise: Issue a 'HOLD' directive to maintain the current instance pool state.",
    "",
    "EXECUTIVE REPORTING STRUCTURE:",
    "Generate a clean, professional markdown executive boardroom brief containing the following four headers:",
    "### 🤖 Capacity Orchestration Executive Decision",
    "State your final decision clearly (e.g., ACTION REQUIRED: SCALE UP FLEET or SYSTEM STABLE: HOLD CAPACITY) alongside the detected traffic pattern archetype (BURST, PERIODIC, or RAMP).",
    "### 📊 Polished Metric Evaluation",
    "Provide a bulleted list breaking down: Current CPU Average, Predicted 15-Minute CPU Load, and Active Replica Pool Count.",
    "### 🏎️ Hardware-Aware FinOps & Carbon Footprint",
    "State the current AMD EPYC Power Draw in Watts and explain how this scaling decision optimizes performance-per-watt metrics, lowers total cost of ownership (TCO), or minimizes environmental carbon footprints.",
    "### 🧠 Technical & Business Justification",
    "Explain the 'Why' behind your decision in clear corporate business terms. Map the risk of doing nothing (e.g., SLA dropouts or lost transactions vs. idle server cash burn) so judges see your enterprise value."
]

# 3. Instantiate the complete Agno Multi-Agent framework using your VLLM parameters
agent = Agent(
    name="AegisScale Orchestration Core",
    model=VLLM(
        id="Qwen3-4B",
        base_url="http://localhost:8000/v1",
        api_key="abc-123",
    ),
    tools=[fetch_latest_cluster_metrics], # Hooks your API connection tool directly to the agent
    instructions=capacity_planning_instructions, # Passes the comprehensive system prompt rule matrix
    markdown=True,
)

if __name__ == "__main__":
    print("⏳ Running AegisScale Autonomous Infrastructure Assessment loop...")
    
    # Prompt the agent to evaluate the cluster state and automatically generate its analytical breakdown
    agent.print_response(
        "Execute a comprehensive infrastructure capacity audit. Fetch the newest polished telemetry, "
        "evaluate the look-ahead prediction parameters, and output your formal scaling directive and business justification."
    )
