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
# 1. PREMIUM CYBER-PERIWINKLE ENTERPRISE DARK THEME OVERRIDE (CSS INJECTION)
# ==============================================================================
st.set_page_config(
    page_title="Groclake AIOps: Enterprise Agent Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded", 
)

groclake_theme_css = """
<style>
    /* Global Application Canvas Configuration */
    .stApp {
        background: linear-gradient(180deg, #090B14 0%, #0E111F 100%) !important;
        color: #A2B1CD !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    /* Left Sidebar Navigation Drawer Overrides */
    div[data-testid="stSidebar"] {
        background-color: #0D101E !important;
        border-right: 1px solid rgba(139, 92, 246, 0.15) !important;
    }
    .sidebar-brand {
        font-size: 1.35rem;
        font-weight: 700;
        color: #A855F7 !important;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    .sidebar-arabic-subtitle {
        font-size: 0.75rem;
        color: #6B7280;
        margin-bottom: 1.5rem;
    }
    
    /* Top Management Control Breadcrumb Strip */
    .top-breadcrumb-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0E1224;
        padding: 0.85rem 1.5rem;
        border-bottom: 1px solid rgba(139, 92, 246, 0.15);
        margin-bottom: 1.5rem;
        border-radius: 6px;
    }
    .breadcrumb-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .top-action-pills {
        display: flex;
        gap: 0.75rem;
        align-items: center;
    }
    .pill-btn {
        background: #161B33 !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        color: #C3DAF9 !important;
        padding: 0.35rem 0.85rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .pill-btn.primary {
        background: #7C3AED !important;
        border: 1px solid #8B5CF6 !important;
        color: #FFFFFF !important;
    }
    
    /* High-Fidelity Enterprise Token Management Cards (Emulating Image Layout) */
    .agent-registry-card {
        background: #11152C !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4) !important;
        margin-bottom: 1rem;
        position: relative;
    }
    .card-badge {
        position: absolute;
        top: 12px;
        left: 12px;
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        text-transform: uppercase;
    }
    .card-badge.locked {
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
    }
    .agent-avatar-frame {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7C3AED 0%, #06B6D4 100%);
        margin: 0.5rem auto 1rem auto;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.75rem;
        box-shadow: 0 0 15px rgba(124, 58, 237, 0.4);
    }
    .agent-card-name {
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.25rem;
    }
    .agent-card-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #A855F7;
        margin-bottom: 0.1rem;
    }
    .agent-card-subtitle {
        font-size: 0.75rem;
        color: #6B7280;
        margin-bottom: 0.75rem;
    }
    .agent-card-desc {
        font-size: 0.8rem;
        color: #A2B1CD;
        line-height: 1.4;
        margin-bottom: 1rem;
        height: 40px;
    }
    .agent-card-meta {
        border-top: 1px solid rgba(255,255,255,0.05);
        padding-top: 0.75rem;
        font-size: 0.7rem;
        color: #64748B;
        display: flex;
        justify-content: space-between;
    }
    
    /* General Glassmorphic Display Canvas Widgets */
    .workspace-display-widget {
        background: rgba(17, 21, 44, 0.75) !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        border-radius: 8px !important;
        padding: 1.25rem !important;
        margin-bottom: 1rem;
    }
    
    /* Dedicated Base Embedded Terminal Tray Wrapper */
    .terminal-console-panel {
        background: #05070F !important;
        border: 1px solid rgba(6, 182, 212, 0.25) !important;
        border-left: 4px solid #06B6D4 !important;
        border-radius: 4px !important;
        padding: 1rem !important;
        margin-top: 1.5rem;
    }

    /* Operational Highlighting Overrides */
    .text-anomaly { color: #EF4444 !important; font-weight: 700; }
    .text-steady { color: #10B981 !important; font-weight: 700; }
    .text-scaling { color: #A855F7 !important; font-weight: 700; }
    
    h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 700 !important; }
</style>
"""
st.markdown(groclake_theme_css, unsafe_allow_html=True)

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
            "cpu_history": [87.18],
            "node_history": [3],
            "current_telemetry": {
                "cpu_avg": 87.18,
                "memory_avg": 207.43,
                "amd_epyc_power_watts": 337.95,
                "carbon_estimate_kg_per_h": 0.1352,
                "request_rate": 4731,
                "latency_ms": 14,
                "slo_violation_score": 0.88,
                "timestamp": time.strftime("%H:%M:%S"),
            },
            "dna_profile": {
                "type": "STEADY_STATE",
                "confidence": 0.31,
                "burstiness": 0.92,
                "predictability": 0.12,
            },
            "anomaly_report": {
                "anomaly_detected": True,
                "classification": "MEMORY_OVERFLOW",
                "confidence_score": 0.99,
                "root_signal": "Cluster Memory Utilization Matrix Over 200%",
            },
            "capacity_plan": {
                "recommended_pods": 4,
                "recommended_nodes": 4,
                "predicted_latency_ms": 4,
                "confidence": 0.95,
                "future_cpu_forecast": 97.64,
            },
            "hardware_finops": {
                "approved": False,
                "optimized_nodes": 4,
                "hardware_selection": "AMD_EPYC_CPU",
                "efficiency_justification": "Mismatched execution target. The logic layer forced workload to baseline AMD EPYC CPU cores, triggering immediate memory contention.",
                "critic_confidence": 0.96,
            },
            "safety_clearance": {
                "clearance": False,
                "final_nodes_count": 3,
                "digital_twin_simulated_risk": "HIGH",
                "postmortem_markdown": "### 🛑 Digital Twin Scaling Contention Analysis\n- **Contention Trace:** High-load structural mismatch detected.\n- **Risk Factor:** vCPU saturation forecast modeling hits 97.64% combined with severe memory bounds.",
            },
            "incident_history": [
                {"timestamp": "12:15:22", "vector": "Memory Pool Exhaustion", "impact": "SLO Bound Breach", "status": "VETOED"},
                {"timestamp": "11:40:10", "vector": "BURST Traffic Spike", "impact": "vCPU Throttle Risk", "status": "SCALE_OUT"},
                {"timestamp": "10:05:45", "vector": "Data Pipeline Contention", "impact": "Latency Deviation", "status": "MITIGATED"}
            ],
            "postmortems": [
                {"timestamp": "12:15:22", "report": "### 🛑 Resource Exhaustion Warning\nMemory pool hit <span class='text-anomaly'>207.43%</span>. Workload forced to standard EPYC cores instead of Instinct offloading targets."},
                {"timestamp": "11:40:10", "report": "### ⚡ BURST Pattern Impact Analysis\nInbound transaction rate reached <span class='text-scaling'>4,731 RPS</span>. Recommended scaling up pods from 3 to 4 immediately."},
                {"timestamp": "10:05:45", "report": "### ✅ Pipeline Matrix Balance Complete\nSystem stabilization pass performed. Baseline transactional states converged successfully."}
            ],
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

# Initialize Agent primitives
recon_agent = Agent(
    name="Aegis Recon Ops",
    model=VLLM(id="Qwen3-4B", base_url="http://localhost:8000/v1", api_key="abc-123"),
    instructions=[
        "You are an elite, covert Tactical Reconnaissance AI Agent named AEGIS-RECON.",
        "Your role is to read the raw data cluster json state and provide briefings inside the Groclake control shell.",
        "Speak with intense, quiet confidence, like a tactical mission controller.",
        "CRITICAL: Keep your thought phase extremely short (max 1 sentence) or omit it completely.",
        "Use custom styled spans cleanly: <span class='text-anomaly'>VALUE</span> for critical alarms, <span class='text-steady'>VALUE</span> for clear metrics, and <span class='text-scaling'>VALUE</span> for hardware updates."
    ],
    markdown=True
)

# ==============================================================================
# 3. NON-THREADED AGNO CLIENT CONVERSION BRIDGE (LIVE AUTOSCALING RUNNER)
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
# 4. SIDEBAR NAVIGATION CONTROLLERS (VERBATIM FROM IMAGE REFERENCE)
# ==============================================================================
with st.sidebar:
    st.markdown('<div class="sidebar-brand">Groclake AIOps</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-arabic-subtitle">مساعد التدقيق الأوتوماتيكي</div>', unsafe_allow_html=True)
    
    navigation_route = st.radio(
        "NAVIGATION ROUTE MAP",
        options=[
            "💬 Copilot Channel",
            "📊 Executive Dashboard",
            "⚡ Interventions",
            "📋 SOSE Summary",
            "🤖 Agent Registry (Active)",
            "📚 Intent Library",
            "📦 Resource Provisioning",
            "🛠️ Build & Deploy",
            "🧩 Model Registry",
            "🔀 Data & Pipelines",
            "🛡️ Controls & Compliance",
            "📉 RCA & Self-Healing",
            "🔄 Dynamic Workflows"
        ],
        index=4 # Defaults active selection target right to the Agent Registry view from image_880031.jpg
    )
    st.markdown("---")
    st.caption(f"Active Session: User Manoj Gupta\nRole: Cluster Administrator\nTarget: amd-prod-cluster-01")

# ==============================================================================
# 5. TOP BAR REPLICATION (BREADCRUMBS & ACTION PILLS FROM IMAGE REFERENCE)
# ==============================================================================
st.markdown(f"""
<div class="top-breadcrumb-bar">
    <div class="breadcrumb-title">
        📁 Agent Management / <span style="color:#A855F7;">{navigation_route[2:]}</span>
    </div>
    <div class="top-action-pills">
        <div class="pill-btn">⚙️ APC Management</div>
        <div class="pill-btn">🗄️ Agentlake Management</div>
        <div class="pill-btn primary">+ Create Agent</div>
        <div style="margin-left: 1rem; font-size:0.85rem; font-weight:600; color:#FFFFFF;">👤 Manoj Gupta</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. DYNAMIC INTERACTIVE WORKSPACE DRAWER BY USAGE PROFILE
# ==============================================================================

# ------------------------------------------------------------------------------
# PROFILE 1: AGENT REGISTRY VIEWPORT (EXACT EMULATION OF CARD GRID IN IMAGE)
# ------------------------------------------------------------------------------
if "Agent Registry" in navigation_route:
    st.markdown("## Agent Registry")
    st.markdown("<p style='color:#64748B; margin-top:-0.5rem; margin-bottom:1.5rem;'>Manage and trace your autonomous cluster optimization and scaling agents.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='display:flex; gap:0.5rem; margin-bottom:1.5rem;'>
        <span style='background:#7C3AED; color:white; padding:0.2rem 0.75rem; border-radius:4px; font-size:0.8rem; font-weight:600;'>All Agents</span>
        <span style='background:#161B33; color:#A2B1CD; padding:0.2rem 0.75rem; border-radius:4px; font-size:0.8rem;'>AI Agents</span>
        <span style='background:#161B33; color:#A2B1CD; padding:0.2rem 0.75rem; border-radius:4px; font-size:0.8rem;'>Human Agents</span>
        <span style='background:#161B33; color:#10B981; padding:0.2rem 0.75rem; border-radius:4px; font-size:0.8rem; font-weight:600;'>Active</span>
        <span style='background:#161B33; color:#6B7280; padding:0.2rem 0.75rem; border-radius:4px; font-size:0.8rem;'>Inactive</span>
    </div>
    """, unsafe_allow_html=True)
    
    card_col_1, card_col_2, card_col_3 = st.columns(3)
    
    with card_col_1:
        st.markdown(f"""
        <div class="agent-registry-card">
            <div class="card-badge">Active</div>
            <div class="agent-avatar-frame">👤</div>
            <div class="agent-card-name">John</div>
            <div class="agent-card-title">Groclake Deployment Manager</div>
            <div class="agent-card-subtitle">General Operations</div>
            <div class="agent-card-desc">Deploys code across compute node grids. Currently holding {state.get('active_nodes', 3)} active replicas.</div>
            <div class="agent-card-meta">
                <span>ID: 6ac542...</span>
                <span>Target: AMD_EPYC_CPU</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with card_col_2:
        st.markdown(f"""
        <div class="agent-registry-card">
            <div class="card-badge locked">Active & Locked</div>
            <div class="agent-avatar-frame">🤖</div>
            <div class="agent-card-name">Greg</div>
            <div class="agent-card-title">Groclake Trigger Manager</div>
            <div class="agent-card-subtitle">General Operations</div>
            <div class="agent-card-desc">Monitors transient connection requests. Currently handling a peak wave of <span class='text-anomaly'>{telemetry.get('request_rate')} RPS</span>.</div>
            <div class="agent-card-meta">
                <span>ID: 4b8920...</span>
                <span>Flag: BURST_PATTERN</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with card_col_3:
        st.markdown(f"""
        <div class="agent-registry-card">
            <div class="card-badge locked">Active & Locked</div>
            <div class="agent-avatar-frame">⚙️</div>
            <div class="agent-card-name">Piyush</div>
            <div class="agent-card-title">Groclake Agentsmith Agent</div>
            <div class="agent-card-subtitle">General Operations</div>
            <div class="agent-card-desc">Logs pipeline telemetry variables. Detected an active <span class='text-anomaly'>Memory Wall of {telemetry.get('memory_avg')}%</span>.</div>
            <div class="agent-card-meta">
                <span>ID: 4397d0...</span>
                <span>Metric Pool: Anomaly</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PROFILE 2: INTERVENTIONS VIEWPORT (ACTUAL AUTOSCALING RUNTIME INTERACTION PIPELINE)
# ------------------------------------------------------------------------------
elif "Interventions" in navigation_route:
    st.markdown("## Live Auto-Scaling Intervention Bay")
    st.caption("Direct integration hub with the Agno Team AgentOS orchestrator engine to compute cluster adjustments.")

    action_btn_placeholder = st.empty()
    status_box = st.empty()

    st.markdown("#### Live Orchestrator Trace Log Terminal")
    log_terminal = st.empty()

    st.markdown("#### Synthesized Live Output")
    output_response_box = st.empty()

    # The actual functionality executed live inside your new image-consistent layout
    if action_btn_placeholder.button("🚀 RUN COMPREHENSIVE AUTOSCALING EVALUATION PASS", use_container_width=True):
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
                output_response_box.markdown(f'<div style="background:#05070F; padding:1rem; border-radius:8px; color:#E2E8F0; line-height:1.6; border-left: 3px solid #7C3AED;">{full_text_accumulator}🖨️</div>', unsafe_allow_html=True)
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

# ------------------------------------------------------------------------------
# PROFILE 3: EXECUTIVE DASHBOARD / COMMAND CENTER VIEWPORT
# ------------------------------------------------------------------------------
elif "Dashboard" in navigation_route:
    st.markdown("## Infrastructure Command Center Vitals")
    
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        st.markdown(f'<div class="workspace-display-widget"><h5>Cluster Memory Saturation</h5><h2 class="text-anomaly">{telemetry.get("memory_avg")}%</h2><p style="font-size:0.8rem; color:#6B7280;">Critical Boundary Breached</p></div>', unsafe_allow_html=True)
    with col_v2:
        st.markdown(f'<div class="workspace-display-widget"><h5>Predictive 15m CPU Load</h5><h2 class="text-anomaly">{plan.get("future_cpu_forecast")}%</h2><p style="font-size:0.8rem; color:#6B7280;">ML Lookahead Horizon Threshold</p></div>', unsafe_allow_html=True)
    with col_v3:
        st.markdown(f'<div class="workspace-display-widget"><h5>Application Load Volume</h5><h2 class="text-scaling">{telemetry.get("request_rate"):,} RPS</h2><p style="font-size:0.8rem; color:#6B7280;">Transient BURST Wave Triggered</p></div>', unsafe_allow_html=True)

    st.markdown("#### Real-time Node Pool Capacity Curves")
    chart_data = pd.DataFrame({
        "vCPU Load": [41.2, 43.5, 42.1, 44.8, 42.0, float(telemetry.get("cpu_avg", 87.18))],
        "Memory Saturation": [62.4, 65.1, 62.0, 68.5, 62.0, float(telemetry.get("memory_avg", 207.43))],
        "Safety Base Ceiling": [80.0, 80.0, 80.0, 80.0, 80.0, 80.0]
    }, index=["11:55", "12:00", "12:05", "12:10", "12:15", "12:20"])
    st.area_chart(chart_data, height=260)

# ------------------------------------------------------------------------------
# PROFILE 4: INTERACTIVE RCA & ANOMALY SPIKES VIEWPORT
# ------------------------------------------------------------------------------
elif "RCA" in navigation_route:
    st.markdown("## Interactive Spike Diagnostics & Root-Cause Center")
    st.caption("Click individual row incidents to instantly pull their multi-agent automated diagnosis.")
    
    trace_matrix_table = pd.DataFrame([
        {"Target Frame": "12:20 (Current Core Overflow)", "Inbound Load": "4,731 RPS", "Memory Peak": "207.43%", "Pool Diagnostics": "CRITICAL ALARM"},
        {"Target Frame": "11:40 (Transient Scaling Wave)", "Inbound Load": "3,890 RPS", "Memory Peak": "92.11%", "Pool Diagnostics": "STABLE_MARGIN"},
        {"Target Frame": "10:05 (Optimal Baseline Run)", "Inbound Load": "1,220 RPS", "Memory Peak": "61.40%", "Pool Diagnostics": "STABLE_MARGIN"}
    ])
    
    selected_row_event = st.dataframe(
        trace_matrix_table, 
        use_container_width=True, 
        hide_index=True, 
        on_select="rerun", 
        selection_mode="single-row"
    )
    
    event_lookup_dictionary = {
        0: {
            "title": "Incident ID: INC-0912A (Vector Compute Target Mismatch)",
            "cause": "Intensive data processing burst directed to baseline AMD EPYC CPU calculation loops instead of active GPU chains, causing an immediately unsustainable memory overflow score of 207.43%.",
            "fix": "Enforce hardware offloading directives to map vector layers to AMD Instinct GPU node arrays immediately."
        },
        1: {
            "title": "Incident ID: INC-0842B (Distributed Endpoint Connection Spike)",
            "cause": "Automated pipeline components checking in synchronously. Absorbed cleanly but hit safety ceiling boundaries.",
            "fix": "Stagger automated worker node cron targets by a randomized 30-second sliding offset factor."
        },
        2: {
            "title": "Incident ID: Baseline Nominal Trace",
            "cause": "System parameters running well inside default engineered scaling ranges.",
            "fix": "No corrective infrastructure actions required."
        }
    }
    
    active_row_pointer = 0
    if selected_row_event and len(selected_row_event.get("selection", {}).get("rows", [])) > 0:
        active_row_pointer = selected_row_event["selection"]["rows"][0]
        
    active_event_context = event_lookup_dictionary[active_row_pointer]
    
    col_rca1, col_rca2 = st.columns(2)
    with col_rca1:
        st.markdown(f'<div class="workspace-display-widget" style="border-left: 4px solid #EF4444 !important;"><h5>🔍 Root-Cause Analysis</h5><p style="font-size:0.9rem; font-weight:700; color:white;">{active_event_context["title"]}</p><p style="font-size:0.85rem; line-height:1.5;">{active_event_context["cause"]}</p></div>', unsafe_allow_html=True)
    with col_rca2:
        st.markdown(f'<div class="workspace-display-widget" style="border-left: 4px solid #10B981 !important;"><h5>⚙️ Advised Action Script</h5><p style="font-size:0.9rem; font-weight:700; color:white;">Remediation Protocol</p><p style="font-size:0.85rem; line-height:1.5;">{active_event_context["fix"]}</p></div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PROFILE 5: SEARCHABLE LOG LEDGER ARCHIVE VIEWPORT
# ------------------------------------------------------------------------------
elif "SOSE Summary" in navigation_route:
    st.markdown("## Searchable Incident Ledger History Archive")
    
    search_filter_string = st.text_input("🔍 Live lookup keyword scanner (Filter logs instantly by typing words like 'OOM', 'EPYC', 'Burst'):").strip().lower()
    
    raw_incidents_matrix = state.get("incident_history", [])
    raw_postmortems_matrix = state.get("postmortems", [])
    
    if search_filter_string:
        raw_incidents_matrix = [i for i in raw_incidents_matrix if search_filter_string in i['vector'].lower() or search_filter_string in i['impact'].lower()]
        raw_postmortems_matrix = [p for p in raw_postmortems_matrix if search_filter_string in p['report'].lower()]
        
    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        st.markdown("#### Matched Structural Ledger Logs")
        if raw_incidents_matrix:
            st.dataframe(pd.DataFrame(raw_incidents_matrix), use_container_width=True, hide_index=True)
        else:
            st.info("No matching timeline fields discovered.")
    with col_l2:
        st.markdown("#### Matched Multi-Agent Evaluation Traces")
        if raw_postmortems_matrix:
            for report_segment in raw_postmortems_matrix:
                with st.expander(f"Report Target Frame Meta: {report_segment['timestamp']}"):
                    st.markdown(report_segment["report"], unsafe_allow_html=True)
        else:
            st.info("No text files conform to filter parameters.")

# ------------------------------------------------------------------------------
# PROFILE 6: HARDWARE PROVISIONING HUB
# ------------------------------------------------------------------------------
else:
    st.markdown(f"## Hardware Provisioning Hub: AMD Core Metrics")
    st.markdown(f"**Selected Architecture Profile Allocation target:** `{finops.get('hardware_selection')}`")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown(f"<div class='workspace-display-widget'><h5>Environmental Core Impact Statement</h5><p style='font-size:0.85rem; line-height:1.5;'>{finops.get('efficiency_justification')}</p><p>Simulated Risk Factor: <span class='text-anomaly'>{safety.get('digital_twin_simulated_risk')}</span></p></div>", unsafe_allow_html=True)
    with col_f2:
        power_curve_data = pd.DataFrame({
            "Timeline": ["11:55", "12:00", "12:05", "12:10", "12:15", "12:20"], 
            "Socket Consumption (Watts)": [337.95, 337.90, 338.02, 337.85, 337.92, float(telemetry.get("amd_epyc_power_watts", 337.95))]
        }).set_index("Timeline")
        st.bar_chart(power_curve_data, height=140)

# ==============================================================================
# 7. INTEGRATED BASE SHELL TRAY (PERSISTENT SECURE RECON INTELLIGENCE BED)
# ==============================================================================
st.markdown("<br/>### 🖥️ Integrated AEGIS-RECON Debugging Console Shell Container", unsafe_allow_html=True)
st.markdown('<div class="terminal-console-panel">', unsafe_allow_html=True)

# Initialize background shell states
if "enterprise_shell_history" not in st.session_state:
    st.session_state["enterprise_shell_history"] = [
        {"role": "assistant", "content": "⚡ *AIOps Core Connected. Remote telemetry parsed successfully. Awaiting dispatch queries, Operator.*"}
    ]
    
# Render active console logs
for conversation_message in st.session_state["enterprise_shell_history"]:
    with st.chat_message(conversation_message["role"]):
        st.markdown(conversation_message["content"], unsafe_allow_html=True)
        
# Collect active field command prompt queries
operator_console_prompt = st.chat_input("Inject shell query regarding cluster deployment status...")
if operator_console_prompt:
    with st.chat_message("user"):
        st.markdown(operator_console_prompt)
    st.session_state["enterprise_shell_history"].append({"role": "user", "content": operator_console_prompt})
    
    composite_prompt_context = f"""
    CURRENT STATE ARCHITECTURE VALUES METRIC DICTIONARY:
    {json.dumps(state, indent=2)}
    
    DISPATCH CONSOLE PROMPT:
    {operator_console_prompt}
    """
    
    with st.chat_message("assistant"):
        live_accumulation_placeholder = st.empty()
        streaming_text_accumulator = ""
        
        response_stream_token_generator = recon_agent.run(composite_prompt_context, stream=True)
        for response_chunk in response_stream_token_generator:
            isolated_token_content = ""
            if hasattr(response_chunk, "content") and response_chunk.content:
                isolated_token_content = response_chunk.content
            elif isinstance(response_chunk, str):
                isolated_token_content = response_chunk
                
            streaming_text_accumulator += isolated_token_content
            live_accumulation_placeholder.markdown(streaming_text_accumulator, unsafe_allow_html=True)
            
        finalized_shell_response_string = streaming_text_accumulator
        
    st.session_state["enterprise_shell_history"].append({"role": "assistant", "content": finalized_shell_response_string})

st.markdown('</div>', unsafe_allow_html=True)

# Auto-refresh sequence pacing loop
time.sleep(3)
st.rerun()
