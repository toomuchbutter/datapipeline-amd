import asyncio
from agno.team import Team
from agno.os import AgentOS
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

agent_os = AgentOS(teams=[orchestrator_team])
app = agent_os.get_app()
if __name__ == "__main__":
    agent_os.serve(app="orchestrator:app", reload=True, port=8002)

