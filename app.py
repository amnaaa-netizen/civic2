"""
Civic Issue Reporter — Advanced Streamlit UI
Premium design with glassmorphism, animations, and interactive charts.
"""

import os
import random
import time
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

# ============================================================
# LOAD API KEY (works local + cloud)
# ============================================================
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============================================================
# IMPORT BACKEND
# ============================================================
from utils.vision import classify_issue
from utils.router import route_to_department
from utils.database import (
    init_db,
    create_complaint,
    get_all_complaints,
    update_status,
    get_stats,
)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Civic Issue Reporter — Pro",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SESSION STATE
# ============================================================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# ============================================================
# INIT DB
# ============================================================
init_db()
os.makedirs("uploads", exist_ok=True)

# ============================================================
# THEME COLORS
# ============================================================
if st.session_state.theme == "light":
    BG_GRADIENT = "linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #dbeafe 100%)"
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    CARD_BG = "rgba(255, 255, 255, 0.75)"
    CARD_BORDER = "rgba(255, 255, 255, 0.9)"
    SHADOW = "0 8px 32px rgba(30, 58, 138, 0.12)"
else:
    BG_GRADIENT = "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%)"
    TEXT_PRIMARY = "#f1f5f9"
    TEXT_SECONDARY = "#94a3b8"
    CARD_BG = "rgba(30, 41, 59, 0.75)"
    CARD_BORDER = "rgba(148, 163, 184, 0.2)"
    SHADOW = "0 8px 32px rgba(0, 0, 0, 0.4)"

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {BG_GRADIENT};
        background-attachment: fixed;
    }}
    .main h1, .main h2, .main h3, .main h4, .main p, .main label {{
        color: {TEXT_PRIMARY} !important;
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%);
        border-right: 1px solid rgba(6, 182, 212, 0.3);
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    h1 {{ color: {TEXT_PRIMARY} !important; font-weight: 800 !important; }}
    h2, h3 {{ color: {TEXT_PRIMARY} !important; font-weight: 700 !important; }}

    .glass-card {{
        background: {CARD_BG};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid {CARD_BORDER};
        border-radius: 20px;
        padding: 24px;
        box-shadow: {SHADOW};
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .glass-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(6, 182, 212, 0.25);
    }}
    [data-testid="stMetric"] {{
        background: {CARD_BG};
        backdrop-filter: blur(20px);
        border: 1px solid {CARD_BORDER};
        border-radius: 16px;
        padding: 20px;
        box-shadow: {SHADOW};
        transition: transform 0.3s ease;
    }}
    [data-testid="stMetric"]:hover {{ transform: translateY(-4px); }}
    [data-testid="stMetric"] label {{
        color: {TEXT_SECONDARY} !important; font-weight: 600 !important;
    }}
    [data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {TEXT_PRIMARY} !important; font-weight: 800 !important;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, #1e3a8a 0%, #06b6d4 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 700;
        font-size: 15px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px rgba(6, 182, 212, 0.3);
        width: 100%;
    }}
    .stButton > button:hover {{
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 28px rgba(6, 182, 212, 0.5);
    }}
    [data-testid="stFileUploader"] {{
        background: {CARD_BG};
        backdrop-filter: blur(20px);
        border: 2px dashed #06b6d4;
        border-radius: 16px;
        padding: 20px;
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: #1e3a8a;
        box-shadow: 0 0 24px rgba(6, 182, 212, 0.3);
    }}
    .ticket-badge {{
        background: linear-gradient(135deg, #1e3a8a 0%, #06b6d4 100%);
        color: white;
        padding: 16px 32px;
        border-radius: 50px;
        font-weight: 800;
        font-size: 22px;
        display: inline-block;
        margin: 16px 0;
        box-shadow: 0 8px 32px rgba(6, 182, 212, 0.5);
        animation: pulse 2s infinite;
        letter-spacing: 0.05em;
    }}
    @keyframes pulse {{
        0%, 100% {{ box-shadow: 0 8px 32px rgba(6, 182, 212, 0.5); }}
        50% {{ box-shadow: 0 8px 48px rgba(6, 182, 212, 0.8); }}
    }}
    .status-pill {{
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        color: white;
        letter-spacing: 0.03em;
    }}
    .severity-critical {{ background: linear-gradient(90deg, #dc2626, #ef4444); }}
    .severity-high {{ background: linear-gradient(90deg, #ea580c, #f97316); }}
    .severity-medium {{ background: linear-gradient(90deg, #ca8a04, #eab308); }}
    .severity-low {{ background: linear-gradient(90deg, #16a34a, #22c55e); }}

    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .fade-in {{ animation: fadeInUp 0.6s ease-out; }}

    .stProgress > div > div > div {{
        background: linear-gradient(90deg, #1e3a8a 0%, #06b6d4 100%);
        border-radius: 10px;
    }}
    .hero {{
        background: linear-gradient(135deg, #1e3a8a 0%, #06b6d4 100%);
        color: white;
        padding: 32px;
        border-radius: 24px;
        margin-bottom: 24px;
        box-shadow: 0 12px 40px rgba(6, 182, 212, 0.3);
    }}
    .hero h1 {{ color: white !important; margin: 0; font-size: 36px; }}
    .hero p {{ color: #bae6fd; margin: 8px 0 0 0; font-size: 16px; }}

    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 24px 0;">
            <div style="font-size: 48px;">🏙️</div>
            <h2 style="color: white; font-size: 22px; margin: 8px 0;">Civic Issue Reporter</h2>
            <p style="color: #06b6d4; font-size: 12px; font-weight: 600;
                      letter-spacing: 0.1em;">PRO EDITION</p>
        </div>
        <hr style="border-color: rgba(6, 182, 212, 0.3);"/>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "**Navigation**",
        ["🏠 Home", "📸 Report Issue", "📋 Track Complaints", "📊 Dashboard"],
    )

    st.markdown(
        '<hr style="border-color: rgba(6, 182, 212, 0.3);"/>',
        unsafe_allow_html=True,
    )

    theme_choice = st.toggle(
        "🌙 Dark Mode",
        value=(st.session_state.theme == "dark"),
    )
    new_theme = "dark" if theme_choice else "light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.markdown(
        """
        <hr style="border-color: rgba(6, 182, 212, 0.3);"/>
        <div style="padding: 10px 0; font-size: 12px; color: #bae6fd;">
            <p>🤖 <b>Gemini AI</b> Powered</p>
            <p>📊 <b>Streamlit</b> + <b>Plotly</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# HELPERS
# ============================================================
def get_status_color(status):
    return {
        "Submitted": "#f59e0b",
        "Acknowledged": "#3b82f6",
        "In Progress": "#8b5cf6",
        "Resolved": "#10b981",
    }.get(status, "#64748b")


def get_severity_class(severity):
    return {
        "Critical": "severity-critical",
        "High": "severity-high",
        "Medium": "severity-medium",
        "Low": "severity-low",
    }.get(severity, "severity-medium")


def render_stat_card(icon, label, value, color):
    st.markdown(
        f"""
        <div class="glass-card" style="text-align:center; padding: 20px;">
            <div style="font-size: 36px; margin-bottom: 8px;">{icon}</div>
            <div style="font-size: 32px; font-weight: 800; color: {color};">
                {value}
            </div>
            <div style="font-size: 13px; color: {TEXT_SECONDARY}; font-weight: 600;
                        text-transform: uppercase; letter-spacing: 0.05em;">
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE 0: HOME
# ============================================================
if page == "🏠 Home":
    st.markdown(
        """
        <div class="hero fade-in">
            <h1>🏙️ Civic Issue Reporter</h1>
            <p>AI-powered civic complaint system — Snap, Classify, Route, Track</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats = get_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_stat_card("📋", "Total", stats["Total"], "#1e3a8a")
    with col2:
        render_stat_card("✅", "Resolved", stats["Resolved"], "#10b981")
    with col3:
        render_stat_card("⚙️", "In Progress", stats["In Progress"], "#8b5cf6")
    with col4:
        render_stat_card("⏳", "Pending", stats["Submitted"], "#f59e0b")

    st.markdown("<br>", unsafe_allow_html=True)

    if stats["Total"] == 0:
        st.info("📌 No complaints yet. Go to **📸 Report Issue** to file your first one.")

    st.markdown("### 🚀 How It Works")
    steps = [
        ("📸", "Snap a Photo", "Citizen uploads photo of the issue"),
        ("🤖", "AI Classifies", "Gemini Vision identifies the problem"),
        ("🧠", "Smart Routing", "AI routes to correct department"),
        ("📋", "Get Ticket", "Unique tracking ID generated"),
        ("✅", "Track Progress", "Real-time status updates"),
    ]
    for icon, title, desc in steps:
        st.markdown(
            f"""
            <div class="glass-card" style="padding: 16px;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div style="font-size: 32px;">{icon}</div>
                    <div>
                        <div style="font-weight: 700; font-size: 16px;
                                    color: {TEXT_PRIMARY};">
                            {title}
                        </div>
                        <div style="font-size: 13px; color: {TEXT_SECONDARY};">
                            {desc}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# PAGE 1: REPORT ISSUE
# ============================================================
elif page == "📸 Report Issue":
    st.markdown(
        """
        <div class="hero">
            <h1>📸 Report a Civic Issue</h1>
            <p>Upload a photo — AI will classify and route it in seconds</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 📷 Step 1: Upload Photo")

        uploaded_file = st.file_uploader(
            "Drop your photo here",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )

        if uploaded_file:
            img_path = os.path.join("uploads", uploaded_file.name)
            with open(img_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.image(Image.open(img_path), use_column_width=True)

        st.markdown("### 📍 Step 2: Location")
        col_lat, col_lon = st.columns(2)
        with col_lat:
            lat = st.number_input("Latitude", value=24.8607, format="%.6f")
        with col_lon:
            lon = st.number_input("Longitude", value=67.0011, format="%.6f")

    with col2:
        st.markdown("### 🤖 Step 3: AI Analysis")

        if uploaded_file and st.button("🚀 Analyze & Route", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown("🧠 **Analyzing image...**")
            for i in range(30):
                time.sleep(0.02)
                progress_bar.progress(i + 1)

            try:
                vision_result = classify_issue(img_path)
            except Exception as e:
                st.error(f"❌ Vision API error: {e}")
                st.stop()

            status_text.markdown("🏢 **Routing to department...**")
            for i in range(30, 70):
                time.sleep(0.02)
                progress_bar.progress(i + 1)

            try:
                routing_result = route_to_department(vision_result["description"])
            except Exception as e:
                st.error(f"❌ Routing error: {e}")
                st.stop()

            status_text.markdown("🎫 **Generating ticket...**")
            for i in range(70, 100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)

            progress_bar.empty()
            status_text.empty()

            st.markdown(
                f"""
                <div class="glass-card fade-in">
                    <div style="display: flex; justify-content: space-between;
                                align-items: center; margin-bottom: 16px;">
                        <h4 style="margin: 0; color: {TEXT_PRIMARY};">✅ Detected</h4>
                        <span class="status-pill {get_severity_class(vision_result['severity'])}">
                            {vision_result['severity']}
                        </span>
                    </div>
                    <div style="display: grid; gap: 12px;">
                        <div>
                            <div style="font-size:12px; color:{TEXT_SECONDARY};
                                        text-transform:uppercase; font-weight:600;">
                                Category
                            </div>
                            <div style="font-size:18px; font-weight:700;
                                        color:{TEXT_PRIMARY};">
                                {vision_result['category']}
                            </div>
                        </div>
                        <div>
                            <div style="font-size:12px; color:{TEXT_SECONDARY};
                                        text-transform:uppercase; font-weight:600;">
                                Description
                            </div>
                            <div style="font-size:14px; color:{TEXT_PRIMARY};">
                                {vision_result['description']}
                            </div>
                        </div>
                        <div>
                            <div style="font-size:12px; color:{TEXT_SECONDARY};
                                        text-transform:uppercase; font-weight:600;">
                                Confidence
                            </div>
                            <div style="font-size:24px; font-weight:800;
                                        color:#06b6d4;">
                                {vision_result['confidence']}%
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="glass-card fade-in">
                    <h4 style="margin-top:0; color:{TEXT_PRIMARY};">🏢 Routed To</h4>
                    <div style="font-size:18px; font-weight:700; color:#06b6d4;
                                margin-bottom:12px;">
                        {routing_result['department']}
                    </div>
                    <div style="display:flex; gap:12px; flex-wrap:wrap;">
                        <span class="status-pill" style="background:#1e3a8a;">
                            ⏱️ SLA: {routing_result['sla']}
                        </span>
                        <span class="status-pill" style="background:#059669;">
                            📧 {routing_result['contact']}
                        </span>
                    </div>
                    <p style="margin-top:12px; color:{TEXT_SECONDARY}; font-size:13px;
                              font-style:italic;">
                        💡 {routing_result['reason']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            ticket_id = create_complaint(
                category=vision_result["category"],
                severity=vision_result["severity"],
                description=vision_result["description"],
                lat=lat,
                lon=lon,
                department=routing_result["department"],
            )

            st.markdown(
                f"""
                <div style="text-align:center;">
                    <div class="ticket-badge">🎫 {ticket_id}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.success("✅ Complaint filed successfully!")
            st.balloons()


# ============================================================
# PAGE 2: TRACK COMPLAINTS
# ============================================================
elif page == "📋 Track Complaints":
    st.markdown(
        """
        <div class="hero">
            <h1>📋 Track Your Complaints</h1>
            <p>Real-time status of every filed complaint</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    complaints = get_all_complaints()

    if not complaints:
        st.info("📭 No complaints filed yet. Go to **📸 Report Issue** to file one.")
    else:
        col1, col2 = st.columns([1, 2], gap="large")

        with col1:
            st.markdown("### 🎫 Select Ticket")
            ticket = st.selectbox(
                "Choose ticket",
                [c["ticket_id"] for c in complaints],
                label_visibility="collapsed",
            )

            selected = next(c for c in complaints if c["ticket_id"] == ticket)
            status_color = get_status_color(selected["status"])

            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="font-size:12px; color:{TEXT_SECONDARY};
                                text-transform:uppercase; font-weight:600;">
                        Status
                    </div>
                    <span class="status-pill" style="background:{status_color};
                          margin-top:8px;">
                        {selected['status']}
                    </span>
                    <hr style="border-color:rgba(148,163,184,0.2); margin:16px 0;"/>
                    <div style="display:grid; gap:12px;">
                        <div>
                            <div style="font-size:12px; color:{TEXT_SECONDARY};
                                        font-weight:600;">CATEGORY</div>
                            <div style="font-weight:700; color:{TEXT_PRIMARY};">
                                {selected['category']}
                            </div>
                        </div>
                        <div>
                            <div style="font-size:12px; color:{TEXT_SECONDARY};
                                        font-weight:600;">SEVERITY</div>
                            <span class="status-pill {get_severity_class(selected['severity'])}">
                                {selected['severity']}
                            </span>
                        </div>
                        <div>
                            <div style="font-size:12px; color:{TEXT_SECONDARY};
                                        font-weight:600;">FILED</div>
                            <div style="color:{TEXT_PRIMARY}; font-size:13px;">
                                {selected['created_at'][:10]}
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown("### 📄 Details")

            st.markdown(
                f"""
                <div class="glass-card">
                    <h4 style="margin-top:0; color:{TEXT_PRIMARY};">
                        Ticket <code style="background:#1e3a8a; color:white;
                        padding:2px 8px; border-radius:6px;">{selected['ticket_id']}</code>
                    </h4>
                    <div style="display:grid; gap:16px; margin-top:16px;">
                        <div>
                            <div style="font-size:12px; color:{TEXT_SECONDARY};
                                        text-transform:uppercase; font-weight:600;">
                                📝 Description
                            </div>
                            <div style="color:{TEXT_PRIMARY}; margin-top:4px;">
                                {selected['description']}
                            </div>
                        </div>
                        <div>
                            <div style="font-size:12px; color:{TEXT_SECONDARY};
                                        text-transform:uppercase; font-weight:600;">
                                🏢 Department
                            </div>
                            <div style="color:{TEXT_PRIMARY}; font-weight:600;
                                        margin-top:4px;">
                                {selected['department']}
                            </div>
                        </div>
                        <div>
                            <div style="font-size:12px; color:{TEXT_SECONDARY};
                                        text-transform:uppercase; font-weight:600;">
                                📍 Location
                            </div>
                            <div style="color:{TEXT_PRIMARY}; margin-top:4px;">
                                {selected['latitude']:.4f}, {selected['longitude']:.4f}
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("### 🕐 Progress Timeline")
            status_options = ["Submitted", "Acknowledged", "In Progress", "Resolved"]
            current_idx = status_options.index(selected["status"])

            timeline_html = '<div class="glass-card">'
            for i, s in enumerate(status_options):
                is_done = i <= current_idx
                color = "#10b981" if is_done else "#cbd5e1"
                icon = "✅" if is_done else "⭕"
                weight = "700" if is_done else "400"
                timeline_html += f"""
                <div style="display:flex; align-items:center; gap:12px;
                            padding:8px 0; color:{color}; font-weight:{weight};">
                    <span style="font-size:18px;">{icon}</span>
                    <span>{s}</span>
                </div>
                """
            timeline_html += "</div>"
            st.markdown(timeline_html, unsafe_allow_html=True)

            progress = (current_idx + 1) / len(status_options)
            st.progress(progress)

            st.markdown("### 🔄 Update Status")
            new_status = st.selectbox(
                "New status", status_options, index=current_idx,
                label_visibility="collapsed"
            )
            if st.button("💾 Update Status"):
                update_status(ticket, new_status)
                st.success(f"Status updated to **{new_status}**")
                st.rerun()


# ============================================================
# PAGE 3: DASHBOARD
# ============================================================
elif page == "📊 Dashboard":
    st.markdown(
        """
        <div class="hero">
            <h1>📊 City Officials Dashboard</h1>
            <p>Real-time analytics and insights for all civic complaints</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    complaints = get_all_complaints()

    if not complaints:
        st.info("📊 No data yet. File some complaints first.")
    else:
        df = pd.DataFrame(complaints)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_stat_card("📋", "Total", len(df), "#1e3a8a")
        with col2:
            render_stat_card("✅", "Resolved",
                             len(df[df["status"] == "Resolved"]), "#10b981")
        with col3:
            render_stat_card("⚙️", "In Progress",
                             len(df[df["status"] == "In Progress"]), "#8b5cf6")
        with col4:
            render_stat_card("⏳", "Pending",
                             len(df[df["status"] == "Submitted"]), "#f59e0b")

        st.markdown("<br>", unsafe_allow_html=True)

        colA, colB = st.columns(2)

        with colA:
            st.markdown("### 📊 By Category")
            cat_counts = df["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            fig = px.bar(
                cat_counts, x="Count", y="Category", orientation="h",
                color="Count", color_continuous_scale=["#06b6d4", "#1e3a8a"],
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color=TEXT_PRIMARY,
                showlegend=False, height=340,
                margin=dict(l=0, r=0, t=20, b=0),
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)

        with colB:
            st.markdown("### ⚠️ By Severity")
            sev_counts = df["severity"].value_counts().reset_index()
            sev_counts.columns = ["Severity", "Count"]
            color_map = {
                "Critical": "#dc2626", "High": "#ea580c",
                "Medium": "#eab308", "Low": "#16a34a",
            }
            fig = px.pie(
                sev_counts, values="Count", names="Severity",
                color="Severity", color_discrete_map=color_map, hole=0.6,
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color=TEXT_PRIMARY,
                height=340, margin=dict(l=0, r=0, t=20, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🗺️ Issue Heatmap")
        fig = px.scatter_mapbox(
            df, lat="latitude", lon="longitude",
            color="severity",
            hover_data=["ticket_id", "category", "status"],
            color_discrete_map={
                "Critical": "#dc2626", "High": "#ea580c",
                "Medium": "#eab308", "Low": "#16a34a",
            },
            zoom=11, height=450,
        )
        fig.update_layout(
            mapbox_style="open-street-map",
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📋 All Complaints")
        col_exp1, col_exp2 = st.columns([4, 1])
        with col_exp2:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export CSV", csv, "complaints.csv", "text/csv",
                use_container_width=True,
            )
        st.dataframe(df, use_container_width=True, hide_index=True)
