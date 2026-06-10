from agno.agent import Agent
from agno.models.vllm import VLLM

agent = Agent(
        model=VLLM(
            id="Qwen3-4B",
            base_url="http://localhost:8000/v1",
            api_key="abc-123",
            ),
        markdown=True
        )
agent.print_response("Share a 1 min horror story")
