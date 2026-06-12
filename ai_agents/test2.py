import asyncio
from agno.client import AgentOSClient
from agno.run.team import RunCompletedEvent, RunContentEvent

async def main():
    client = AgentOSClient(base_url="http://localhost:8002")
    async for event in client.run_team_stream(
            team_id="workload-dna-orchestrator-core",
            message="Initiate comprehensive live telemetry evaluation sequence for current port 8050 systems.",
            ):
        if isinstance(event, RunContentEvent):
            print(event.content, end="", flush=True)

asyncio.run(main())
