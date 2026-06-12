import json
import requests
from agno.models.vllm import VLLM

# Shared vLLM initialization pointing to your local Qwen3 instance
shared_model = VLLM(
    id="Qwen3-4B", 
    base_url="http://localhost:8000/v1", 
    api_key="abc-123",
    # max_tokens=6024,
)

def fetch_live_telemetry_from_bridge() -> str:
    """Queries the running aiis-data-layer on port 8050 for fresh metrics.
    
    Returns:
        str: Minified JSON string containing active port telemetry or error state.
    """
    try:
        r = requests.get("http://localhost:8050/api/v1/metrics/latest", timeout=3)
        if r.status_code == 200:
            return json.dumps(r.json())
        return json.dumps({"error": f"API port error: {r.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"Failed connection to data layer: {str(e)}"})
