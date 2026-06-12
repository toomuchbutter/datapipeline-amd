import asyncio
from datetime import datetime
import json
import os
import time
import numpy as np
import pandas as pd
import streamlit as st
from agno.client import AgentOSClient

# Import core Agno agent primitives and the VLLM model constructor
from agno.agent import Agent
from agno.models.vllm import VLLM

# ==============================================================================
# 0. CLIENT INFRASTRUCTURE OVERRIDES: LOCAL VLLM ISOLATION GATES
# ==============================================================================

os.environ["OPENAI_BASE_URL"] = "http://localhost:8000/v1"

# ==============================================================================
# 1. PREMIUM CYBER-INDUSTRIAL DARK THEME OVERRIDE (CSS INJECTION)
# ==============================================================================
st.set_page_config(
    page_title="AegisScale AI: Autonomous AIOps Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded", 
)

agentops_theme_css = """
<style>
    /* Global Application Base Canvas Overrides */
    .stApp {
        background: linear-gradient(135deg, #070A12 0%, #0C111D 100%) !important;
        color: #94A3B8 !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    /* Clean, Translucent High-Tech Container Boxes (Glassmorphism Effect) */
    div.stMetric, div.stAlert, .stTabs, div[data-testid="stExpander"], .agent-node, .stat-panel {
        background: rgba(13, 19, 32, 0.8) !important;
        border: 1px solid rgba(0, 223, 137, 0.1) !important;
        border-radius: 14px !important;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6) !important;
        backdrop-filter: blur(8px);
        padding: 1.5rem !important;
        margin-bottom: 1rem;
    }

    /* Streamlit Chat Message Box Dark Theme Overrides */
    div[data-testid="stChatMessage"] {
        background-color: rgba(11, 16, 27, 0.9) !important;
        border: 1px solid rgba(56, 189, 248, 0.15) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 0.85rem !important;
        padding: 1.25rem !important;
    }
    div[data-testid="stChatMessage"] div.stMarkdown p,
    div[data-testid="stChatMessage"] div.stMarkdown li {
        color: #E2E8F0 !important;
        line-height: 1.6 !important;
    }
    div[data-testid="stChatMessage"] div.stMarkdown h1,
    div[data-testid="stChatMessage"] div.stMarkdown h2,
    div[data-testid="stChatMessage"] div.stMarkdown h3 {
        color: #FFFFFF !important;
        margin-top: 0.5rem !important;
    }

    /* Elegant, Compact Format for AI Reason/Think Blocks */
    think, .thinking {
        display: block;
        color: #64748B !important;
        font-style: italic;
        background: #050810 !important;
        border-left: 2px solid #38BDF8 !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: 4px;
        margin-bottom: 0.75rem;
        font-size: 0.85rem;
    }

    /* Customization Matrix for the High-Fidelity KPI Grid Tile System */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .grid-tile {
        background: #111726;
        border: 1px solid rgba(56, 189, 248, 0.1);
        border-radius: 8px;
        padding: 1.25rem;
        text-align: left;
    }
    .grid-tile.header {
        grid-column: span 4;
        background: rgba(17, 24, 39, 0.9);
        border-bottom: 2px solid rgba(0, 223, 137, 0.3);
    }
    .grid-tile.kpi-row-2 { background: #0E1321; }
    
    .tile-label { font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
    .tile-value { font-size: 2.25rem; font-weight: 700; color: #FFFFFF; margin-top: 0.5rem; }
    .tile-subtext { font-size: 0.8rem; color: #94A3B8; margin-top: 0.25rem; }
    .tile-subtext.neon { color: #00DF89; }
    .tile-subtext.blue { color: #38BDF8; }
    .tile-subtext.orange { color: #F59E0B; }

    /* Core Action Banner - Critical Red Alerts */
    .governor-block {
        background: radial-gradient(circle at top left, rgba(239, 68, 68, 0.12), rgba(13, 19, 32, 0.95)) !important;
        border: 1px solid rgba(239, 68, 68, 0.35) !important;
        border-left: 6px solid #EF4444 !important;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Grid Layouts for Autonomous Agent Boardroom Cards */
    .agent-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.25rem;
    }
    .agent-node {
        border-top: 4px solid #00DF89 !important;
        position: relative;
    }
    .agent-node.vetoed {
        border-top: 4px solid #F59E0B !important;
    }
    .agent-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #FFFFFF;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .agent-status-tag {
        font-size: 0.7rem;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        background: rgba(0, 223, 137, 0.15);
        color: #00DF89;
        font-weight: 600;
    }
    .agent-status-tag.warn {
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
    }
    
    /* Subjective Dialogue Stream Components */
    .subjective-bubble {
        background: #090D16;
        border-left: 3px solid #00DF89;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1rem;
        font-size: 0.85rem;
        color: #E2E8F0;
        line-height: 1.5;
    }
    .subjective-bubble.warn {
        border-left-color: #F59E0B;
    }

    /* Progress Meters (Resource Allocations style) */
    .allocation-row {
        margin-bottom: 0.75rem;
    }
    .allocation-label-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #64748B;
        margin-bottom: 0.25rem;
    }
    .allocation-bar-bg {
        background: #161F30;
        border-radius: 4px;
        height: 8px;
        width: 100%;
        overflow: hidden;
    }
    .allocation-bar-fill {
        background: linear-gradient(90deg, #00DF89, #38BDF8);
        height: 100%;
    }
    
    /* Secret Agent Intelligence Sidebar Console Layout Tweaks */
    div[data-testid="stSidebar"] {
        background-color: #594ba0 !important;
        border-right: 1px solid rgba(0, 223, 137, 0.15) !important;
    }
    
    /* Fix squished markdown rendering within the chat interface */
    div[data-testid="stChatMessage"] div.stMarkdown p {
        line-height: 1.6 !important;
        margin-bottom: 1rem !important;
    }
    div[data-testid="stChatMessage"] div.stMarkdown li {
        margin-bottom: 0.5rem !important;
    }
    
    .text-anomaly { color: #EF4444 !important; font-weight: 700; }
    .text-steady { color: #00DF89 !important; font-weight: 700; }
    .text-scaling { color: #38BDF8 !important; font-weight: 700; }

    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #64748B !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border: none !important;
        padding: 12px 24px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00DF89 !important;
        border-bottom: 2px solid #00DF89 !important;
    }
    
    h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
    .section-divider { border: 0; border-top: 2px solid rgba(56, 189, 248, 0.1); margin: 2rem 0; }
</style>
"""
st.markdown(agentops_theme_css, unsafe_allow_html=True)

# ==============================================================================
# 2. RUNTIME SYNCHRONIZED STORAGE CONNECTOR (CACHE READER)
# ==============================================================================
def pull_boardroom_state() -> dict:
    cache_path = "system_state.json"
    if not os.path.exists(cache_path):
        return {
            "system_health": "REJECTED",
            "active_nodes": 3,
            "cost_saved_usd": 142.50,
            "timestamps": [time.strftime("%H:%M:%S")],
            "cpu_history": [87.92],
            "node_history": [3],
            "current_telemetry": {
                "cpu_avg": 87.2,
                "memory_avg": 68.38,
                "amd_epyc_power_watts": 339.8,
                "carbon_estimate_kg_per_h": 0.1359,
                "request_rate": 4731,
                "latency_ms": 0,
                "slo_violation_score": 0.0,
                "timestamp": time.strftime("%H:%M:%S"),
            },
            "dna_profile": {
                "type": "STEADY_STATE",
                "confidence": 0.00,
                "burstiness": 0.12,
                "predictability": 0.88,
            },
            "anomaly_report": {
                "anomaly_detected": False,
                "classification": "NONE",
                "confidence_score": 0.98,
                "root_signal": "Telemetry Normal Matrix",
            },
            "capacity_plan": {
                "recommended_pods": 4,
                "recommended_nodes": 4,
                "predicted_latency_ms": 12,
                "confidence": 0.95,
                "future_cpu_forecast": 0.0,
            },
            "hardware_finops": {
                "approved": True,
                "optimized_nodes": 4,
                "hardware_selection": "AMD_EPYC_CPU",
                "efficiency_justification": "Stable baseline transactional load detected. Processing routed directly to AMD EPYC CPU cores to optimize efficiency variables.",
                "critic_confidence": 0.96,
            },
            "safety_clearance": {
                "clearance": True,
                "final_nodes_count": 4,
                "digital_twin_simulated_risk": "LOW",
                "postmortem_markdown": "### ✅ Digital Twin Clearance Summary\n- All telemetry matrices conform completely to standard thresholds.",
            },
            "incident_history": [],
            "postmortems": [],
        }
    try:
        with open(cache_path, "r") as f:
            return json.load(f)
    except:
        time.sleep(0.1)
        with open(cache_path, "r") as f:
            return json.load(f)

state = pull_boardroom_state()
telemetry = state.get("current_telemetry", {})
dna = state.get("dna_profile", {})
anomaly = state.get("anomaly_report", {})
plan = state.get("capacity_plan", {})
finops = state.get("hardware_finops", {})
safety = state.get("safety_clearance", {})

# ==============================================================================
# 3. SECRET AGENT COVERT INTELLIGENCE CHANNEL (LOCAL VLLM QWEN CORE)
# ==============================================================================
with st.sidebar:
    st.markdown("###CODENAME: AEGIS-RECON")
    st.caption("Tactical Field Reconnaissance & Threat Assessment Console")
    st.markdown("---")
    
    # Local VLLM model instantiation configured for streaming execution parameters
    recon_agent = Agent(
        name="Aegis Recon Ops",
        model=VLLM(id="Qwen3-4B", base_url="http://localhost:8000/v1", api_key="abc-123"),
        instructions=[
            "You are an elite, covert Tactical Reconnaissance AI Agent named AEGIS-RECON.",
            "Your role is to read the raw data cluster json state provided by the user and give a sleek intelligence briefing.",
            "Speak with an intense, quiet confidence, like a secret agent or tactical mission controller.",
            "CRITICAL: Keep your thought/reasoning phase extremely short (max 1 sentence) or omit it completely to ensure rapid briefings.",
            "CRITICAL: Always use proper markdown spacing. Ensure there are distinct empty line breaks between paragraphs, headers, and bullet points.",
            "CRITICAL: Never wrap markdown code blocks (like ```markdown ... ```) around your entire response. Output standard document lines directly.",
            "Use espionage/tactical phrasing: 'Operational vector scanned', 'SLA vulnerability detected', 'Countermeasures advised'.",
            "MATCH APPLICATION HIGHLIGHT CSS: Integrate raw inline span tags matching the UI styling directly inside your text text headings or bullet values. "
            "CRITICAL: Do NOT wrap markdown markdown bold identifiers (**) around HTML span tags. Use them cleanly like this: "
            "- Operational Vector Scanned: <span class='text-steady'>amd-prod-cluster-01</span>"
            "- Critical Warning: <span class='text-anomaly'>CPU Utilization approaching limits</span>"
            "- Core Hardware Shift: <span class='text-scaling'>Route to AMD Instinct GPU</span>"
        ],
        markdown=True
    )

    if "recon_chat_history" not in st.session_state:
        st.session_state["recon_chat_history"] = [
            {"role": "assistant", "content": "⚡ *Recon transmission open. Cluster telemetry indexed. Standing by for situational briefing queries, Commander.*"}
        ]

    for msg in st.session_state["recon_chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)

    user_query = st.chat_input("Ask Recon Agent about live system threat levels...")
    
    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state["recon_chat_history"].append({"role": "user", "content": user_query})
        
        contextual_prompt = f"""
        CURRENT CLUSTER METRICS INGEST:
        {json.dumps(state, indent=2)}
        
        OPERATOR TACTICAL QUERY:
        {user_query}
        """
        
        with st.chat_message("assistant"):
            # Setup custom live-updating placeholder container
            message_placeholder = st.empty()
            full_response = ""
            
            response_stream = recon_agent.run(contextual_prompt, stream=True)
            for chunk in response_stream:
                content = ""
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                elif isinstance(chunk, str):
                    content = chunk
                
                full_response += content
                # Overrides native st.write_stream to allow raw HTML parsing during stream iteration
                message_placeholder.markdown(full_response, unsafe_allow_html=True)
                
            recon_response = full_response
                
        st.session_state["recon_chat_history"].append({"role": "assistant", "content": recon_response})

# ==============================================================================
# 4. NON-THREADED AGNO CLIENT CONVERSION BRIDGE
# ==============================================================================
def get_agno_events_sync(payload_msg):
    """Bypasses reverse proxy filters, manually step-advances the Agno async generator"""
    client = AgentOSClient(base_url="http://127.0.0.1:8002")
    loop = asyncio.new_event_loop()

    try:
        async_gen = client.run_team_stream(
            team_id="workload-dna-orchestrator-core", message=payload_msg
        )
        while True:
            try:
                event = loop.run_until_complete(async_gen.__anext__())
                yield type(event).__name__, event
            except StopAsyncIteration:
                break
    except Exception as e:
        yield "TeamRunError", e
    finally:
        loop.close()

# ==============================================================================
# 5. MAIN CHANNELS TABBED VIEWPORT CHASSIS
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏥 Channel 1: Command Center",
    "🧠 Channel 2: AI Boardroom Intelligence",
    "📜 Channel 3: Incident Postmortem Ledger",
    "🏎️ Channel 4: AMD Hardware Analytics",
])

# ------------------------------------------------------------------------------
# CHANNEL 1: INFRASTRUCTURE COMMAND CENTER (REAL-TIME VITALS & CURVES)
# ------------------------------------------------------------------------------
with tab1:
    st.markdown("### Real-Time Cluster Telemetry & Environmental Metrics")

    anomaly_status = anomaly.get("anomaly_detected", False)
    anomaly_text = "⚠️ ANOMALY DETECTED" if anomaly_status else "✅ INTEGRITY GATES CLEAR"
    anomaly_class = "text-anomaly" if anomaly_status else "text-steady"

    html_grid_a = f"""
    <div class="grid-container">
        <div class="grid-tile">
            <div class="tile-label">Workload Pattern Fingerprint</div>
            <div class="tile-value text-steady">{dna.get('type', 'STEADY_STATE')}</div>
            <div class="tile-subtext neon">DNA Confidence Index: {dna.get('confidence', 0.0):.2f}</div>
        </div>
        <div class="grid-tile">
            <div class="tile-label">Cluster CPU Load (Avg)</div>
            <div class="tile-value">{telemetry.get('cpu_avg', 0.0):.1f}%</div>
            <div class="tile-subtext blue">Target Capacity Limit: 80%</div>
        </div>
        <div class="grid-tile">
            <div class="tile-label">Active Compute fleet Scale</div>
            <div class="tile-value">{state.get('active_nodes', 4)} Instances</div>
            <div class="tile-subtext blue">Allocated Across AMD Cluster Pool</div>
        </div>
        <div class="grid-tile">
            <div class="tile-label">Environmental Integrity Monitor</div>
            <div class="tile-value {anomaly_class}">{anomaly_text}</div>
            <div class="tile-subtext orange">Scan Source: Anomaly Intel Agent</div>
        </div>
    </div>
    """
    st.markdown(html_grid_a, unsafe_allow_html=True)

    current_health = "SCALING_ACTIVE" if "SCALING" in state.get("system_health") else "HEALTHY"
    health_text = "🟡 TUNING LOAD" if current_health == "SCALING_ACTIVE" else "🟢 OPERATIONAL"

    html_grid_b = f"""
    <div class="grid-container">
        <div class="grid-tile kpi-row-2">
            <div class="tile-label">Application Transaction Rate</div>
            <div class="tile-value text-steady">{telemetry.get('request_rate', 0):,}<span style="font-size:1.25rem;"> RPS</span></div>
            <div class="tile-subtext blue">Live Inbound Telemetry</div>
        </div>
        <div class="grid-tile kpi-row-2">
            <div class="tile-label">Cluster API Latency (Avg)</div>
            <div class="tile-value text-steady">{telemetry.get('latency_ms', 0):,}<span style="font-size:1.25rem;"> ms</span></div>
            <div class="tile-subtext blue">Real-time Performance Vector</div>
        </div>
        <div class="grid-tile kpi-row-2">
            <div class="tile-label">Model Look-Ahead forecast Horizon</div>
            <div class="tile-value text-scaling">{plan.get('future_cpu_forecast', 0.0):.1f}%</div>
            <div class="tile-subtext orange">ML Predictive CPU saturation [15m]</div>
        </div>
        <div class="grid-tile kpi-row-2">
            <div class="tile-label">Active SLO Violation Score</div>
            <div class="tile-value text-anomaly">{telemetry.get('slo_violation_score', 0.0):.2f}</div>
            <div class="tile-subtext neon">Integrity Gating Status: {health_text}</div>
        </div>
    </div>
    """
    st.markdown(html_grid_b, unsafe_allow_html=True)

    st.markdown("### Multi-Dimensional Performance & Capacity Curves")
    col_chart_1, col_chart_2 = st.columns(2)

    with col_chart_1:
        st.markdown("#### Multivariate Saturation Vectors & System Thrashing Risk")
        if "chart_history" not in st.session_state:
            st.session_state["chart_history"] = pd.DataFrame(
                {
                    "vCPU_Utilization": [41.2, 43.5, 42.1, 44.8, 42.0, 87.2],
                    "Memory_Utilization": [62.4, 62.1, 62.0, 63.5, 62.0, 68.38],
                    "Safety_Threshold_Limit": [80.0, 80.0, 80.0, 80.0, 80.0, 80.0],
                },
                index=["11:00", "11:05", "11:10", "11:15", "11:20", datetime.now().strftime("%H:%M:%S")],
            )

        latest_ts = datetime.now().strftime("%H:%M:%S")
        if latest_ts not in st.session_state["chart_history"].index:
            new_row = pd.DataFrame([{"vCPU_Utilization": float(telemetry.get("cpu_avg", 87.2)), "Memory_Utilization": float(telemetry.get("memory_avg", 68.38)), "Safety_Threshold_Limit": 80.0}], index=[latest_ts])
            st.session_state["chart_history"] = pd.concat([st.session_state["chart_history"], new_row]).tail(30)

        st.area_chart(st.session_state["chart_history"][["vCPU_Utilization", "Safety_Threshold_Limit"]], height=320)
        st.caption("🔴 Load Spike Trace Baseline Ceiling at 80%. Shaded Area indicates an intensive traffic spike detected.")

    with col_chart_2:
        st.markdown("#### AMD Hardware performance-per-Watt and Cost Efficiency Curve")
        tco_dataframe = pd.DataFrame({"Timeline": state.get("timestamps", [datetime.now().strftime("%H:%M:%S")]), "Est. Cost ($/h)": [1.45 for _ in state.get("timestamps", [1])], "AMD Core Efficiency Score (%)": [91.4 for _ in state.get("timestamps", [1])]}).set_index("Timeline")
        st.line_chart(tco_dataframe)
        st.caption("🏎️ AMD Efficiency Score Channel Key: Blue = Est. Cost ($/h) | Neon Green = AMD Core Efficiency Score (%).")

# ------------------------------------------------------------------------------
# CHANNEL 2: AGENTOS INTERACTIVE WORKSPACE GRID (WITH ITERATIVE EVENT LIFECYCLES)
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("### Live Real-Time Boardroom Streaming Terminal")
    st.caption("Direct interface with Agno Team AgentOS Engine via atomic event lifecycle streaming vectors.")

    action_btn_placeholder = st.empty()
    status_box = st.empty()

    st.markdown("#### Live Orchestrator Trace Log")
    log_terminal = st.empty()

    st.markdown("#### Synthesized Live Output")
    output_response_box = st.empty()

    if action_btn_placeholder.button("🚀 INITIATE COMPREHENSIVE LIVE EVALUATION SEQUENCE", use_container_width=True):
        action_btn_placeholder.empty()
        full_text_accumulator = ""
        trace_logs_accumulator = []
        prompt_input = "Initiate comprehensive live telemetry evaluation sequence for current port 8050 systems."

        for event_type, event_data in get_agno_events_sync(prompt_input):
            if event_type == "TeamRunStarted":
                status_box.info("🏁 [TeamRunStarted] Orchestration sequence initiated. Synchronizing node matrices...")
                trace_logs_accumulator.append("🔹 Execution Session Started.")
            elif event_type == "TeamRunContent":
                chunk_content = getattr(event_data, "content", "")
                full_text_accumulator += chunk_content
                output_response_box.markdown(f'<div style="background:#090D16; padding:1rem; border-radius:8px; color:#E2E8F0; line-height:1.6;">{full_text_accumulator}🖨️</div>', unsafe_allow_html=True)
            elif event_type == "TeamRunCompleted":
                status_box.success("🏁 [TeamRunCompleted] Sequence Complete: All multi-agent boardroom evaluation traces captured.")
                trace_logs_accumulator.append("🟩 Run ended with code 0 (Success).")
            elif event_type == "TeamRunError":
                error_msg = str(event_data) if isinstance(event_data, (str, Exception)) else getattr(event_data, "error", "Unknown engine failure.")
                status_box.error(f"❌ [TeamRunError] Critical Pipeline Abort: {error_msg}")
                trace_logs_accumulator.append(f"🟥 CRITICAL ERROR: {error_msg}")
                break
            elif event_type == "TeamToolCallStarted":
                tool_name = getattr(event_data, "tool_name", "Injected Dependency Tool")
                trace_logs_accumulator.append(f"🛠️ [Tool Started] Calling active routine: `{tool_name}`")
            elif event_type == "TeamToolCallCompleted":
                trace_logs_accumulator.append("✅ [Tool Completed] Return parameters synchronized successfully.")
            elif event_type == "TeamReasoningStarted":
                trace_logs_accumulator.append("🧠 [Reasoning Started] Initiating multi-agent look-ahead calculation trees...")
            elif event_type == "TeamReasoningStep":
                reasoning_chunk = getattr(event_data, "content", "")
                trace_logs_accumulator.append(f" 🔍 [Reasoning Step] {reasoning_chunk.strip()}")
            elif event_type == "TeamReasoningCompleted":
                trace_logs_accumulator.append("🎯 [Reasoning Completed] Tree resolution finalized.")

            log_terminal.code("\n".join(trace_logs_accumulator), language="markdown")

        if full_text_accumulator:
            try:
                with open("system_state.json", "r") as f:
                    current_state = json.load(f)
                current_state["postmortems"].append({"timestamp": datetime.now().strftime("%H:%M:%S"), "report": full_text_accumulator})
                current_state["system_health"] = "HEALTHY"
                with open("system_state.json", "w") as f:
                    json.dump(current_state, f, indent=2)
            except Exception as e:
                st.error(f"Post-stream state compilation error: {str(e)}")
        st.rerun()

    st.markdown("---")
    
    if not safety.get("clearance", True):
        html_governor_card = """
        <div class="governor-block">
            <span style="font-size: 0.75rem; text-transform: uppercase; color: #EF4444; letter-spacing:0.12em; font-weight:700;">[ 🛑 AUTOMATED RUNTIME GOVERNOR BLOCK ]</span>
            <div style="font-size: 1.6rem; font-weight:800; color: #FFFFFF; margin-top: 0.25rem; letter-spacing: -0.01em;">MIGRATION TIMEOUT: SAFETY GATES REJECTED</div>
            <div style="font-size: 0.9rem; color: #94A3B8; margin-top: 0.5rem; line-height: 1.6;">
                The <strong>Safety Governor Agent</strong> has vetoed the infrastructure scale-out routine proposed by the planner. Resource migration to AMD Instinct GPU cores is locked until application memory handles are optimized to prevent out-of-memory (OOM) thrashing.
            </div>
        </div>
        """
        st.markdown(html_governor_card, unsafe_allow_html=True)

    col_left_panel, col_right_grid = st.columns([1, 2])
    with col_left_panel:
        st.markdown("### Essential & Resource Gauges")
        st.markdown('<div class="stat-panel"><span class="tile-label" style="color:#64748B;">Total Agent Tasks Processed</span><div class="tile-value" style="font-size:2.5rem; color:#FFF; font-weight:700; margin: 0.5rem 0;">18,832</div><span style="color:#00DF89; font-size:0.8rem; font-weight:600;"> ⬆ +12.4%</span> this tracking week</div>', unsafe_allow_html=True)
        st.markdown("#### Agent Activity Distribution")
        dna_conf, anom_conf, cap_conf, fin_conf = dna.get("confidence", 0.94) * 100, anomaly.get("confidence_score", 0.98) * 100, plan.get("confidence", 0.91) * 100, finops.get("critic_confidence", 0.95) * 100
        for label, val in [("DNA Fingerprint", dna_conf), ("Anomaly Detector", anom_conf), ("Capacity Sizing", cap_conf), ("FinOps Critic", fin_conf)]:
            st.markdown(f'<div class="allocation-row"><div class="allocation-label-row"><span>{label} Confidence</span><span>{val:.1f}%</span></div><div class="allocation-bar-bg"><div class="allocation-bar-fill" style="width: {val}%;"></div></div></div>', unsafe_allow_html=True)

    with col_right_grid:
        st.markdown("### Agent Hand-off Execution Grid")
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.markdown(f'<div class="agent-node"><div class="agent-name"><span>🧬 1. Workload DNA</span><span class="agent-status-tag">ACTIVE</span></div><div style="font-size: 0.8rem; color:#64748B; font-family: monospace;">Archetype: {dna.get("type")}<br/>Burstiness: {dna.get("burstiness")}</div><div class="subjective-bubble"><strong>Subjective Analysis:</strong> Operational fingerprint indicates baseline load convergence metrics are stable.</div></div>', unsafe_allow_html=True)
        with row1_col2:
            st.markdown(f'<div class="agent-node"><div class="agent-name"><span>⚠️ 2. Anomaly Inspector</span><span class="agent-status-tag">SECURE</span></div><div style="font-size: 0.8rem; color:#64748B; font-family: monospace;">Anomaly Found: {str(anomaly.get("anomaly_detected")).lower()}<br/>Target Trace: {anomaly.get("root_signal")}</div><div class="subjective-bubble"><strong>Subjective Analysis:</strong> Baseline signal tracking remains structurally valid. No telemetry leaks detected.</div></div>', unsafe_allow_html=True)
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.markdown(f'<div class="agent-node"><div class="agent-name"><span>🔮 3. Capacity Planner</span><span class="agent-status-tag">COMPUTING</span></div><div style="font-size: 0.8rem; color:#64748B; font-family: monospace;">Target Pods: {plan.get("recommended_pods")}<br/>15m CPU Forecast: {plan.get("future_cpu_forecast")}%</div><div class="subjective-bubble"><strong>Subjective Analysis:</strong> Microservice requirements calculating successfully. Baseline cluster footprint targeted.</div></div>', unsafe_allow_html=True)
        with row2_col2:
            finops_class = "vetoed" if not finops.get("approved", True) else ""
            finops_tag = "VETOED" if not finops.get("approved", True) else "ROUTED"
            st.markdown(f'<div class="agent-node {finops_class}"><div class="agent-name"><span>🏎️ 4. FinOps & Hardware</span><span class="agent-status-tag">{finops_tag}</span></div><div style="font-size: 0.8rem; color:#64748B; font-family: monospace;">Approved: {str(finops.get("approved")).lower()}<br/>Hardware Target: {finops.get("hardware_selection")}</div><div class="subjective-bubble"><strong>Subjective Analysis:</strong> {finops.get("efficiency_justification")}</div></div>', unsafe_allow_html=True)
        
        if safety.get("clearance", True):
            st.success(f"🛡️ **[Agent 5] Safety Governor Gating:** SAFETY VERDICT: APPROVED | Digital Twin simulated workload migration risk profile clear.")
        else:
            st.error("🛡️ **[Agent 5] Safety Governor Gating:** SAFETY VERDICT: REJECTED | Scaling action throttled due to simulated HIGH risk.")

# ------------------------------------------------------------------------------
# CHANNEL 3: INCIDENT POSTMORTEM LEDGER
# ------------------------------------------------------------------------------
with tab3:
    st.header("Incident History & Autonomous Postmortem Ledger")
    col_timeline, col_postmortem = st.columns([2, 3])
    with col_timeline:
        if state.get("incident_history"): st.dataframe(pd.DataFrame(state["incident_history"]), use_container_width=True)
        else: st.info("Log parameters clear. No outstanding system failure metrics indexed.")
    with col_postmortem:
        st.markdown(safety.get("postmortem_markdown"))
        for report in reversed(state.get("postmortems", [])):
            with st.expander(f"📁 Diagnostic Report Timestamp: {report['timestamp']}"): st.markdown(report["report"])

# ------------------------------------------------------------------------------
# CHANNEL 4: AMD HARDWARE ANALYTICS
# ------------------------------------------------------------------------------
with tab4:
    st.header("AMD Hardware Efficiency Center: Performance-per-Watt Metrics")
    col_hd1, col_hardware2 = st.columns(2)
    with col_hd1:
        hardware_matrix = pd.DataFrame({"Timeline": state.get("timestamps", [datetime.now().strftime("%H:%M:%S")]), "Cluster Power Load (W)": [float(telemetry.get("amd_epyc_power_watts", 339.8)) for _ in state.get("timestamps", [1])], "AMD EPYC Efficiency Score (%)": [92.4 for _ in state.get("timestamps", [1])]}).set_index("Timeline")
        st.line_chart(hardware_matrix)
    with col_hardware2:
        core_allocation = pd.DataFrame({"SKU Pool": ["Active Core Splits"], "AMD_EPYC_CPU": [int(state.get("active_nodes", 3))], "AMD_INSTINCT_GPU": [1 if "GPU" in str(finops.get("hardware_selection")) else 0]}).set_index("SKU Pool")
        st.bar_chart(core_allocation)

    st.markdown("---")
    st.markdown("### AegisScale AI Autonomous Confidence Index Registry")
    confidence_grid_html = f"""
    <div class="grid-container">
        <div class="grid-tile header"><div class="tile-label">Agno Team Autonomous Decision Confidence Registry</div></div>
        <div class="grid-tile"><div class="tile-label">Workload DNA</div><div class="tile-value text-steady">{dna.get('confidence', 0.94) * 100:.1f}%</div></div>
        <div class="grid-tile"><div class="tile-label">Anomaly Intel</div><div class="tile-value text-steady">{anomaly.get('confidence_score', 0.98) * 100:.1f}%</div></div>
        <div class="grid-tile"><div class="tile-label">Capacity Planner</div><div class="tile-value text-scaling">{plan.get('confidence', 0.91) * 100:.1f}%</div></div>
        <div class="grid-tile"><div class="tile-label">FinOps Critic</div><div class="tile-value text-scaling">{finops.get('critic_confidence', 0.95) * 100:.1f}%</div></div>
    </div>
    """
    st.markdown(confidence_grid_html, unsafe_allow_html=True)

# Auto-refresh interval framework pacing loop
time.sleep(3)
st.rerun()
