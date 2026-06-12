from agno.agent import Agent
from shared_config import shared_model, fetch_live_telemetry_from_bridge

# 1. DNA Profiler Agent
dna_agent = Agent(
    name="Workload DNA Profiler",
    role="Compute an operational fingerprint from live metrics.",
    model=shared_model,
    tools=[fetch_live_telemetry_from_bridge],
    instructions=[
        "Analyze raw incoming live telemetry from port 8050 using fetch_live_telemetry_from_bridge.",
        "Categorize workload strands into structural classifications.",
        "Output an operational fingerprint. Rely strictly on facts. Minimize token use."
    ],
    markdown=True
)

# 2. Anomaly Agent
anomaly_agent = Agent(
    name="Anomaly Intelligence Inspector",
    role="Scan infrastructure metrics for degradation or resource leaks.",
    model=shared_model,
    tools=[fetch_live_telemetry_from_bridge],
    instructions=[
        "Scan live port 8050 metrics data for resource degradation flags, thrashing, or memory leaks.",
        "Output anomalies using a condensed list format.",
        "If everything operates clean, respond exactly with: {'anomalies': false}."
    ],
    markdown=True
)

# 3. Capacity Agent
capacity_agent = Agent(
    name="Capacity Planner",
    role="Calculate multivariate resource demand targets.",
    model=shared_model,
    tools=[fetch_live_telemetry_from_bridge],
    instructions=[
        "Review current live telemetry and the derived DNA operational fingerprint.",
        "Calculate multivariate resource demand baseline targets (vCPU, Memory, Storage IOPS).",
        "Keep recommendations structural, exact, and concise."
    ],
    markdown=True
)

# 4. FinOps & Hardware Agent
finops_hardware_agent = Agent(
    name="FinOps & AMD Hardware Critic",
    role="Evaluate capacity allocations against financial and specific hardware routing criteria.",
    model=shared_model,
    tools=[fetch_live_telemetry_from_bridge],
    instructions=[
        "Evaluate proposed capacity allocations against corporate budgets.",
        "Enforce specific hardware routing rules strictly:",
        "  - Route high-load, bursty traffic or scaling anomalies to 'AMD_INSTINCT_GPU' server pools.",
        "  - Route standard, steady transactional code to 'AMD_EPYC_CPU' pools to maximize performance-per-watt metrics.",
        "Provide explicit hardware SKU paths based on these rules."
    ],
    markdown=True
)

# 5. Safety Governor Agent
safety_governor = Agent(
    name="Safety Governor & Autonomous Postmortem Generator",
    role="Run stability metrics validations and digital twin clearances.",
    model=shared_model,
    tools=[fetch_live_telemetry_from_bridge],
    instructions=[
        "Review the entire aggregated multi-agent system plan matrix.",
        "Run a fast digital twin safety clearance calculation using live metrics state to verify structural stability.",
        "Output an explicit status: [APPROVED] or [REJECTED] followed by risk metrics."
    ],
    markdown=True
)
# 6. Secret Field Intelligence & Operations Agent
recon_agent = Agent(
    name="AEGIS-RECON Operator",
    role="Extract live infrastructure metrics to deliver tactical field intelligence briefings.",
    model=shared_model,
    tools=[fetch_live_telemetry_from_bridge],
    instructions=[
        "Scan real-time cluster telemetry footprints via fetch_live_telemetry_from_bridge when evaluating incoming operator prompts.",
        "Adopt an elite, covert intelligence operations persona ('Operational vector scanned', 'SLA vulnerability detected', 'Countermeasures compiled').",
        "Translate dense multi-dimensional graphs, safety locks, and capacity bottlenecks into high-impact situational awareness updates.",
        "Omit conversational padding, pleasantries, or generic corporate filler. Keep reports structural, exact, and actionable."
    ],
    markdown=True
    )
