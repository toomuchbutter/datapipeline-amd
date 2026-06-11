import asyncio
from agno.team import Team
from agents_pool import dna_agent, anomaly_agent, capacity_agent, finops_hardware_agent, safety_governor
from shared_config import shared_model

# Construct the hierarchical Orchestrator Team
orchestrator_team = Team(
    name="Workload DNA Orchestrator Core",
    model=shared_model,
    # Injecting the complete specialized engineering pool
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

async def main():
    f = open("chunks_op.txt", mode="w")
    # Execution entrypoint running live analysis across the collective team
    async for event in orchestrator_team.arun(
        "Initiate comprehensive live telemetry evaluation sequence for current port 8050 systems.", 
        stream=True, stream_events=True
    ):
        f.write(str(event)+"\n")
    f.close()
    # you are to yield the event.content, so this functions is actually a generator

asyncio.run(main())

