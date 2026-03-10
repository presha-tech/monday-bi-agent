"""
Monday.com Business Intelligence Agent
Palette: #036DA4 · #5EA3C0 · #B8D9DC · #D8EBE2 · #FDFCE8
"""

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Monday BI Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── FORCE LIGHT THEME EVERYWHERE ── */
html, body, [class*="css"], .stApp {
    background-color: #EEF6FA !important;
    color: #0d2b3e !important;
    font-family: 'Inter', sans-serif;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #036DA4 0%, #024f78 100%) !important;
}
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #FDFCE8 !important;
}
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small {
    color: #B8D9DC !important;
}
[data-testid="stSidebar"] hr {
    border-top: 1px solid rgba(184,217,220,0.4) !important;
}
/* Sidebar inputs */
[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.15) !important;
    color: #FDFCE8 !important;
    border: 1px solid #5EA3C0 !important;
    border-radius: 8px !important;
    caret-color: #FDFCE8 !important;
}
[data-testid="stSidebar"] input::placeholder { color: #B8D9DC !important; }
[data-testid="stSidebar"] .stTextInput label { color: #B8D9DC !important; font-size:0.8rem; font-weight:600; }
/* Sidebar buttons */
[data-testid="stSidebar"] button {
    background: #B8D9DC !important;
    color: #024f78 !important;
    border: none !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] button:hover {
    background: #D8EBE2 !important;
    color: #024f78 !important;
}
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span,
[data-testid="stSidebar"] button div {
    color: #024f78 !important;
}
/* Expander in sidebar */
[data-testid="stSidebar"] .streamlit-expanderHeader,
[data-testid="stSidebar"] .streamlit-expanderHeader p {
    color: #FDFCE8 !important;
    background: rgba(255,255,255,0.1) !important;
    border-radius: 8px;
    border: 1px solid rgba(184,217,220,0.3) !important;
}

/* ── MAIN AREA — ALL TEXT DARK ── */
.main *, .block-container * {
    color: #0d2b3e;
}

/* Header banner */
.bi-header {
    background: linear-gradient(135deg, #036DA4, #5EA3C0);
    border-radius: 14px;
    padding: 26px 32px 22px;
    margin-bottom: 20px;
}
.bi-header h1 { color: #FDFCE8 !important; margin:0; font-size:1.8rem; font-weight:700; }
.bi-header p  { color: #D8EBE2 !important; margin:6px 0 0; font-size:0.95rem; }

/* Feature cards (landing) */
.feat-card {
    background: #ffffff;
    border: 1px solid #B8D9DC;
    border-top: 4px solid #036DA4;
    border-radius: 12px;
    padding: 22px 18px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(3,109,164,0.07);
}
.feat-icon  { font-size:2rem; }
.feat-label { font-size:0.72rem; color:#036DA4 !important; text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-top:8px; }
.feat-desc  { font-size:0.83rem; color:#4a7080 !important; margin-top:6px; }

/* Status pills */
.pill-on  { background:#D8EBE2; color:#035f8e !important; border:1.5px solid #5EA3C0; border-radius:20px; padding:3px 14px; font-size:0.78rem; font-weight:700; display:inline-block; }
.pill-off { background:#fde8e8; color:#a02020 !important; border:1.5px solid #e0a0a0; border-radius:20px; padding:3px 14px; font-size:0.78rem; font-weight:700; display:inline-block; }

/* Chat bubbles */
.user-msg {
    background: linear-gradient(135deg, #036DA4, #5EA3C0);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 8px 0 8px 18%;
    color: #FDFCE8 !important;
    font-size: 0.94rem;
    line-height: 1.55;
}
.user-msg * { color: #FDFCE8 !important; }

/* Assistant chat — use Streamlit's chat_message widget so markdown renders */

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border: 1px solid #B8D9DC;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #5EA3C0 !important;
    border-radius: 7px !important;
    font-weight: 600;
    font-size: 0.9rem;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: #036DA4 !important;
    color: #FDFCE8 !important;
}

/* Metric boxes */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #B8D9DC;
    border-radius: 10px;
    padding: 14px 16px;
    box-shadow: 0 1px 6px rgba(3,109,164,0.07);
}
[data-testid="stMetricLabel"] p { color: #5EA3C0 !important; font-weight:600 !important; font-size:0.78rem !important; }
[data-testid="stMetricValue"]   { color: #036DA4 !important; font-weight:700 !important; }
[data-testid="stMetricDelta"]   { color: #4a7080 !important; }

/* Buttons in main area */
button[kind="primary"], .stButton > button[data-testid*="primary"] {
    background: #036DA4 !important;
    color: #FDFCE8 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
button[kind="secondary"] {
    background: #ffffff !important;
    color: #036DA4 !important;
    border: 1.5px solid #5EA3C0 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

/* Text inputs in main area */
.stTextInput input {
    background: #ffffff !important;
    color: #0d2b3e !important;
    border: 1.5px solid #B8D9DC !important;
    border-radius: 10px !important;
}
.stTextInput input:focus {
    border-color: #036DA4 !important;
    box-shadow: 0 0 0 2px rgba(3,109,164,0.12) !important;
}
.stTextInput label { color: #036DA4 !important; font-weight:600; }

/* Dataframe */
[data-testid="stDataFrame"] { border:1px solid #B8D9DC; border-radius:10px; overflow:hidden; }

/* Alerts / info */
.stAlert { border-radius:10px !important; }
[data-testid="stInfo"] { background:#EEF6FA !important; border-left:4px solid #5EA3C0 !important; color:#0d2b3e !important; }

/* Inline code highlight — blue instead of black */
code, .stMarkdown code {
    background: #B8D9DC !important;
    color: #024f78 !important;
    border-radius: 4px;
    padding: 1px 5px;
}
/* Chat message text that gets highlighted */
.stChatMessage mark,
.stMarkdown mark {
    background: #B8D9DC !important;
    color: #024f78 !important;
}
/* Fix any dark-background spans inside chat */
.stChatMessage span[style*="background"],
.stMarkdown span[style*="background"] {
    background: #5EA3C0 !important;
    color: #FDFCE8 !important;
    border-radius: 4px;
    padding: 1px 4px;
}

/* Headings */
h1,h2,h3,h4 { color:#036DA4 !important; }
p, li, span { color:#0d2b3e; }
.stMarkdown p { color:#0d2b3e !important; }

/* Expander main area */
.streamlit-expanderHeader { background:#ffffff !important; border:1px solid #B8D9DC !important; border-radius:10px !important; color:#036DA4 !important; font-weight:600; }
.streamlit-expanderHeader p { color:#036DA4 !important; }
.streamlit-expanderContent { background:#ffffff !important; border:1px solid #B8D9DC; border-top:none; border-radius:0 0 10px 10px; }

/* Radio */
.stRadio label { color:#0d2b3e !important; }

/* Horizontal rule */
hr { border-top: 1px solid #B8D9DC !important; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── Imports ───────────────────────────────────────────────────────────────────
try:
    from monday_client import MondayClient, DataProcessor
    from analyzer import DataAnalyzer
    from agent import BIAgent
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "connected": False, "deals": [], "work_orders": [],
    "analyzer": None, "agent": None, "messages": [],
    "board_info": {}, "last_loaded": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt(val):
    try: val = float(val)
    except: return "N/A"
    if val >= 1_000_000: return f"${val/1e6:.1f}M"
    if val >= 1_000:     return f"${val/1e3:.0f}K"
    return f"${val:,.0f}"

def connect_and_load(tok, gkey, did, wid):
    with st.spinner("Connecting to Monday.com…"):
        try:
            client = MondayClient(tok)
            ok, msg = client.test_connection()
            if not ok:
                st.error(f"❌ {msg}"); return False
            st.success(f"✅ {msg}")
            st.session_state.board_info = {
                "deals": client.get_board_info(did),
                "work_orders": client.get_board_info(wid),
            }
        except Exception as e:
            st.error(f"❌ {e}"); return False

    with st.spinner("Loading Deals…"):
        try:
            st.session_state.deals = DataProcessor.process_board_items(client.get_all_items(did))
        except Exception as e:
            st.error(f"❌ Deals: {e}"); return False

    with st.spinner("Loading Work Orders…"):
        try:
            st.session_state.work_orders = DataProcessor.process_board_items(client.get_all_items(wid))
        except Exception as e:
            st.error(f"❌ Work Orders: {e}"); return False

    with st.spinner("Initialising AI agent…"):
        try:
            az = DataAnalyzer(st.session_state.deals, st.session_state.work_orders)
            ag = BIAgent(gkey, az)
            st.session_state.analyzer = az
            st.session_state.agent    = ag
            st.session_state.connected   = True
            st.session_state.last_loaded = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages = [{"role":"assistant","content":(
                f"👋 Connected! Loaded **{len(st.session_state.deals)} deals** and "
                f"**{len(st.session_state.work_orders)} work orders**.\n\n"
                "Try asking:\n- *How's our pipeline this quarter?*\n"
                "- *Which sectors are performing best?*\n- *Generate a leadership brief*"
            )}]
        except Exception as e:
            st.error(f"❌ Agent error: {e}"); return False
    return True

def send_message(txt):
    if not txt.strip() or not st.session_state.connected: return
    st.session_state.messages.append({"role":"user","content":txt})
    try:    reply = st.session_state.agent.chat(txt)
    except Exception as e: reply = f"⚠️ Error: {e}"
    st.session_state.messages.append({"role":"assistant","content":reply})

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 BI Agent")
    st.markdown("---")

    if st.session_state.connected:
        st.markdown('<span class="pill-on">● Connected</span>', unsafe_allow_html=True)
        st.caption(f"Loaded {st.session_state.last_loaded}")
        st.markdown(f"Deals: **{len(st.session_state.deals)}**")
        st.markdown(f"Work Orders: **{len(st.session_state.work_orders)}**")
    else:
        st.markdown('<span class="pill-off">● Not Connected</span>', unsafe_allow_html=True)

    st.markdown("---")

    with st.expander("🔑 API Configuration", expanded=not st.session_state.connected):
        monday_tok = st.text_input("Monday.com API Token", type="password", placeholder="Paste token…")
        groq_key   = st.text_input("Groq API Key",         type="password", placeholder="Paste key…")
        deals_id   = st.text_input("Deals Board ID",       placeholder="")
        wo_id      = st.text_input("Work Orders Board ID", placeholder="")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔌 Connect", type="primary", use_container_width=True):
                if not all([monday_tok, groq_key, deals_id, wo_id]):
                    st.error("Fill all four fields.")
                elif not IMPORTS_OK:
                    st.error(f"Import error: {IMPORT_ERROR}")
                else:
                    if connect_and_load(monday_tok, groq_key, deals_id, wo_id):
                        st.rerun()
        with c2:
            if st.button("🔄 Refresh", use_container_width=True, disabled=not st.session_state.connected):
                if connect_and_load(monday_tok, groq_key, deals_id, wo_id):
                    st.rerun()

    st.markdown("---")

    if st.session_state.connected:
        st.markdown("### ⚡ Quick Queries")
        for q in ["Pipeline overview","Q1 2025 pipeline","Energy sector deals",
                  "Win / loss rate","Overdue work orders","Top 10 deals",
                  "Leadership brief","Data quality check"]:
            if st.button(q, key=f"qq_{q}", use_container_width=True):
                send_message(q); st.rerun()
        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.agent: st.session_state.agent.reset_conversation()
            st.rerun()

    st.markdown("---")
    st.caption("Powered by Monday.com · Groq · Streamlit")

# ── MAIN AREA ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bi-header">
  <h1>📊 Monday.com BI Agent</h1>
  <p>AI-powered business intelligence for founders and executives</p>
</div>
""", unsafe_allow_html=True)

if not IMPORTS_OK:
    st.error(f"⚠️ Import error: {IMPORT_ERROR}")
    st.info("Run: `pip install -r requirements.txt`")
    st.stop()

if not st.session_state.connected:
    c1, c2, c3 = st.columns(3)
    for col, icon, label, desc in [
        (c1, "🔍", "Natural Language", "Ask in plain English — no SQL needed"),
        (c2, "🔄", "Live Data",        "Direct Monday.com API, always fresh"),
        (c3, "🧹", "Smart Cleaning",   "Handles messy real-world data gracefully"),
    ]:
        with col:
            st.markdown(f"""
            <div class="feat-card">
              <div class="feat-icon">{icon}</div>
              <div class="feat-label">{label}</div>
              <div class="feat-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.info("👈 Enter your API credentials in the sidebar and click **Connect**.")

    with st.expander("💡 Example questions"):
        for ex in [
            "How's our pipeline for the energy sector this quarter?",
            "What's our win rate and total closed value?",
            "Top 10 deals by value right now?",
            "How many work orders are overdue?",
            "Full sector breakdown across deals and work orders",
            "Generate a leadership briefing note",
            "Any data quality issues I should know about?",
        ]:
            st.markdown(f"- *{ex}*")
    st.stop()

# ── TABS ──────────────────────────────────────────────────────────────────────
t_chat, t_dash, t_data = st.tabs(["💬 Chat", "📈 Dashboard", "🗃️ Raw Data"])

# CHAT -------------------------------------------------------------------------
with t_chat:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">🧑‍💼 {msg["content"]}</div>',
                        unsafe_allow_html=True)
        else:
            with st.chat_message("assistant", avatar="📊"):
                st.markdown(msg["content"])

    st.markdown("---")
    ci, cs = st.columns([5,1])
    with ci:
        user_input = st.text_input("q", placeholder="Ask a business question…",
                                   label_visibility="collapsed", key="chat_input")
    with cs:
        if st.button("Send ➤", type="primary", use_container_width=True):
            if user_input: send_message(user_input); st.rerun()

    st.markdown("---")
    if st.button("📋 Generate Leadership Brief", type="secondary", use_container_width=True):
        send_message("Generate a comprehensive leadership update brief"); st.rerun()

# DASHBOARD -------------------------------------------------------------------
with t_dash:
    if not st.session_state.analyzer:
        st.info("Connect to Monday.com to see the dashboard.")
    else:
        az = st.session_state.analyzer
        import pandas as pd

        st.markdown("### 💼 Pipeline")
        ov = az.pipeline_overview()
        wl = az.won_lost_analysis()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total Deals",     ov["total_deals"])
        c2.metric("Pipeline Value",  fmt(ov["total_pipeline_value"]))
        c3.metric("Avg Deal Size",   fmt(ov["avg_deal_size"]))
        c4.metric("Win Rate",        f"{wl['win_rate_pct']:.1f}%")

        st.markdown("---")
        cl, cr = st.columns(2)
        with cl:
            st.markdown("#### Pipeline by Status")
            if ov["status_distribution"]:
                st.dataframe(pd.DataFrame([
                    {"Status":k,"Count":v}
                    for k,v in sorted(ov["status_distribution"].items(), key=lambda x:-x[1])
                ]), use_container_width=True, hide_index=True)
            else:
                st.info("No status data found.")
        with cr:
            st.markdown("#### Top Sectors by Value")
            if ov["sector_distribution"]:
                st.dataframe(pd.DataFrame([
                    {"Sector":k,"Value":fmt(v)}
                    for k,v in sorted(ov["sector_distribution"].items(), key=lambda x:-x[1])[:10]
                ]), use_container_width=True, hide_index=True)
            else:
                st.info("No sector data detected.")

        st.markdown("---")
        st.markdown("### 🔧 Work Orders")
        wo = az.work_order_overview()
        op = az.operational_health()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total",    wo["total_work_orders"])
        c2.metric("Active",   op["active_work_orders"])
        c3.metric("On Track", op["on_track"])
        c4.metric("⚠️ Overdue", op["overdue"],
                  delta=f"{op['overdue_pct']:.0f}%", delta_color="inverse")

        st.markdown("---")
        st.markdown("### 📅 Current Quarter")
        q = az.quarterly_pipeline()
        c1,c2,c3 = st.columns(3)
        c1.metric(f"{q['quarter']} Deals", q["deals_in_quarter"])
        c2.metric("Value",                fmt(q["total_value"]))
        c3.metric("Missing Close Dates",  q["deals_without_close_date"])

        st.markdown("---")
        st.markdown("### 🔍 Data Quality")
        dq = az.data_quality_report()
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Deals Board**")
            st.markdown(f"- Missing value: **{dq['deals']['missing_value_pct']}%**")
            st.markdown(f"- Missing status: **{dq['deals']['missing_status_pct']}%**")
            st.markdown(f"- Missing sector: **{dq['deals']['missing_sector_pct']}%**")
        with c2:
            st.markdown("**Work Orders Board**")
            st.markdown(f"- Missing value: **{dq['work_orders']['missing_value_pct']}%**")
            st.markdown(f"- Missing status: **{dq['work_orders']['missing_status_pct']}%**")

# RAW DATA --------------------------------------------------------------------
with t_data:
    if not st.session_state.connected:
        st.info("Connect to Monday.com to view raw data.")
    else:
        import pandas as pd
        view = st.radio("View:", ["Deals","Work Orders","Column Mapping"], horizontal=True)
        if view == "Deals":
            st.markdown(f"**{len(st.session_state.deals)} deals loaded**")
            if st.session_state.deals:
                st.dataframe(pd.DataFrame(st.session_state.deals),
                             use_container_width=True, height=500)
        elif view == "Work Orders":
            st.markdown(f"**{len(st.session_state.work_orders)} work orders loaded**")
            if st.session_state.work_orders:
                st.dataframe(pd.DataFrame(st.session_state.work_orders),
                             use_container_width=True, height=500)
        elif view == "Column Mapping":
            st.info("Auto-detected mappings from Monday.com column names to business concepts.")
            if st.session_state.analyzer:
                cm = st.session_state.analyzer.get_column_map_summary()
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown("**Deals Board**")
                    for concept,col in cm["deals_columns_detected"].items():
                        st.markdown(f"- `{concept}` → `{col}`")
                with c2:
                    st.markdown("**Work Orders Board**")
                    for concept,col in cm["work_order_columns_detected"].items():
                        st.markdown(f"- `{concept}` → `{col}`")
