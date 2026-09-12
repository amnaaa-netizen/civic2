"""
Standalone UI Demo for Civic Issue Reporter.
No API key, no database, no backend needed.
Run: streamlit run demo_ui.py
"""

import streamlit as st
from PIL import Image
import pandas as pd
import random
from datetime import datetime, timedelta

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Civic Issue Reporter — Demo",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown(
    """
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Headings */
    h1 { color: #1e3a8a !important; font-weight: 800 !important; }
    h2, h3 { color: #1e40af !important; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #06b6d4 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        transition: transform 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(6, 182, 212, 0.4);
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(30, 58, 138, 0.1);
        border-left: 5px solid #06b6d4;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 12px;
        padding: 16px;
        border: 2px dashed #06b6d4;
    }

    /* Ticket badge */
    .ticket-badge {
        background: linear-gradient(90deg, #1e3a8a 0%, #06b6d4 100%);
        color: white;
        padding: 12px 24px;
        border-radius: 30px;
        font-weight: bold;
        font-size: 20px;
        display: inline-block;
        margin: 10px 0;
    }

    /* Custom card */
    .custom-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 16px;
    }

    /* Status badge */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        color: white;
        font-size: 13px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# FAKE DATA (Mock)
# ============================================================
MOCK_COMPLAINTS = [
    {
        "ticket_id": "CIV-A3F9K2",
        "category": "Pothole",
        "severity": "High",
        "description": "Large pothole on main road filled with water",
        "latitude": 24.8607,
        "longitude": 67.0011,
        "department": "Roads & Public Works Department",
        "status": "In Progress",
        "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
    },
    {
        "ticket_id": "CIV-B7X2M9",
        "category": "Broken Streetlight",
        "severity": "Critical",
        "description": "Streetlight not working near school, dark at night",
        "latitude": 24.8700,
        "longitude": 67.0300,
        "department": "Electricity & Streetlight Department",
        "status": "Resolved",
        "created_at": (datetime.now() - timedelta(days=7)).isoformat(),
    },
    {
        "ticket_id": "CIV-C9K4L1",
        "category": "Garbage Pile",
        "severity": "Medium",
        "description": "Garbage pile on street corner, bad smell",
        "latitude": 24.8500,
        "longitude": 67.0200,
        "department": "Sanitation & Waste Management",
        "status": "Submitted",
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
    },
    {
        "ticket_id": "CIV-D2P8N5",
        "category": "Water Leak",
        "severity": "Critical",
        "description": "Water pipe burst, water wasting on road",
        "latitude": 24.8800,
        "longitude": 67.0500,
        "department": "Water & Sewerage Board",
        "status": "Acknowledged",
        "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
    },
    {
        "ticket_id": "CIV-E5R3T7",
        "category": "Pothole",
        "severity": "Medium",
        "description": "Small pothole near market area",
        "latitude": 24.8650,
        "longitude": 67.0250,
        "department": "Roads & Public Works Department",
        "status": "Resolved",
        "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
    },
    {
        "ticket_id": "CIV-F8W6Y2",
        "category": "Fallen Tree",
        "severity": "High",
        "description": "Tree branch fallen, blocking sidewalk",
        "latitude": 24.8550,
        "longitude": 67.0400,
        "department": "Parks & Horticulture",
        "status": "In Progress",
        "created_at": (datetime.now() - timedelta(days=4)).isoformat(),
    },
]

# Fake AI classification result
MOCK_VISION_RESULT = {
    "category": "Pothole",
    "severity": "High",
    "description": "A large pothole on an asphalt road filled with water, posing risk to vehicles",
    "confidence": 94,
}

MOCK_ROUTING_RESULT = {
    "department": "Roads & Public Works Department",
    "sla": "7 days",
    "contact": "roads@city.gov.pk",
    "reason": "The detected issue is a pothole, which falls under road maintenance handled by this department.",
}


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 20px 0;">
            <h1 style="color: white; font-size: 28px; margin: 0;">🏙️</h1>
            <h2 style="color: white; font-size: 22px; margin: 8px 0;">Civic Issue Reporter</h2>
            <p style="color: #bae6fd; font-size: 13px;">
                Snap → Classify → Route → Track
            </p>
        </div>
        <hr style="border-color: #06b6d4;"/>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "**Navigate**",
        ["📸 Report Issue", "📋 Track Complaints", "📊 Dashboard"],
    )

    st.markdown(
        """
        <hr style="border-color: #06b6d4;"/>
        <div style="padding: 10px 0; font-size: 12px; color: #bae6fd;">
            <p>🤖 Powered by <b>Gemini AI</b></p>
            <p>📊 Built with <b>Streamlit</b></p>
            <p style="color:#fbbf24;">⚠️ DEMO MODE — Fake data</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE 1: REPORT ISSUE
# ============================================================
if page == "📸 Report Issue":
    st.markdown("<h1>📸 Report a Civic Issue</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:16px; color:#475569;'>Upload a photo — AI will classify it and route it to the correct department.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 📷 Step 1: Upload Photo")

        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )

        if uploaded_file:
            st.image(
                Image.open(uploaded_file),
                caption="📌 Uploaded Image",
                use_column_width=True,
            )
        else:
            st.markdown(
                """
                <div class="custom-card" style="text-align:center; padding: 40px;">
                    <h1 style="font-size:50px; margin:0;">🖼️</h1>
                    <p style="color:#64748b;">Upload any image to test the flow</p>
                    <p style="color:#94a3b8; font-size:12px;">(In demo mode, AI result is mocked)</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("### 📍 Step 2: Confirm Location")
        lat = st.number_input("Latitude", value=24.8607, format="%.6f")
        lon = st.number_input("Longitude", value=67.0011, format="%.6f")

    with col2:
        st.markdown("### 🤖 Step 3: AI Analysis")

        if uploaded_file and st.button("🔍 Analyze & Route Issue", type="primary"):
            with st.spinner("🧠 Analyzing image..."):
                import time
                time.sleep(1)
                vision_result = MOCK_VISION_RESULT

            st.markdown(
                f"""
                <div class="custom-card">
                    <h4 style="margin-top:0;">✅ Issue Detected</h4>
                    <p><b>Category:</b> {vision_result['category']}</p>
                    <p><b>Severity:</b> {vision_result['severity']}</p>
                    <p><b>Description:</b> {vision_result['description']}</p>
                    <p><b>Confidence:</b> {vision_result['confidence']}%</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.spinner("🏢 Routing to department..."):
                import time
                time.sleep(1)
                routing_result = MOCK_ROUTING_RESULT

            st.markdown("### 🏢 Department Routing")
            st.info(
                f"**Department:** {routing_result['department']}\n\n"
                f"**SLA:** {routing_result['sla']}\n\n"
                f"**Contact:** {routing_result['contact']}\n\n"
                f"**Reason:** {routing_result['reason']}"
            )

            fake_ticket = "CIV-" + "".join(random.choices("ABCDEF0123456789", k=6))
            st.markdown(
                f"""
                <div style="text-align:center; margin: 20px 0;">
                    <div class="ticket-badge">🎫 Ticket: {fake_ticket}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.success("✅ Complaint filed! (Demo mode)")
            st.balloons()

        elif not uploaded_file:
            st.markdown(
                """
                <div class="custom-card" style="text-align:center; padding: 60px 20px;">
                    <h1 style="font-size: 60px; margin: 0;">📸</h1>
                    <p style="color: #64748b; font-size: 16px;">
                        Upload a photo to see the AI flow
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# PAGE 2: TRACK COMPLAINTS
# ============================================================
elif page == "📋 Track Complaints":
    st.markdown("<h1>📋 Track Your Complaints</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#475569;'>View status of any filed complaint in real time. (Demo data)</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.markdown("### 🎫 Select Ticket")
        ticket = st.selectbox(
            "Choose a ticket ID",
            [c["ticket_id"] for c in MOCK_COMPLAINTS],
            label_visibility="collapsed",
        )

        selected = next(c for c in MOCK_COMPLAINTS if c["ticket_id"] == ticket)

        status_colors = {
            "Submitted": "#f59e0b",
            "Acknowledged": "#3b82f6",
            "In Progress": "#8b5cf6",
            "Resolved": "#10b981",
        }
        status_color = status_colors.get(selected["status"], "#64748b")

        st.markdown(
            f"""
            <div class="custom-card">
                <p><b>Status:</b>
                    <span class="status-badge" style="background:{status_color};">
                        {selected['status']}
                    </span>
                </p>
                <p><b>Category:</b> {selected['category']}</p>
                <p><b>Severity:</b> {selected['severity']}</p>
                <p><b>Filed on:</b> {selected['created_at'][:19]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("### 📄 Complaint Details")

        st.markdown(
            f"""
            <div class="custom-card">
                <h4 style="margin-top:0;">Ticket <code>{selected['ticket_id']}</code></h4>
                <p><b>📝 Description:</b><br>{selected['description']}</p>
                <p><b>🏢 Department:</b> {selected['department']}</p>
                <p><b>📍 Location:</b> ({selected['latitude']}, {selected['longitude']})</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🔄 Update Status")
        status_options = ["Submitted", "Acknowledged", "In Progress", "Resolved"]
        current_idx = status_options.index(selected["status"])

        new_status = st.selectbox("New status", status_options, index=current_idx)

        if st.button("✅ Update Status (Demo)"):
            st.success(f"Status updated to **{new_status}** (demo only — not saved)")

        progress = (status_options.index(selected["status"]) + 1) / len(status_options)
        st.progress(progress)
        st.caption(
            f"Progress: {int(progress * 100)}% — "
            f"{status_options.index(selected['status']) + 1} of {len(status_options)} stages"
        )


# ============================================================
# PAGE 3: DASHBOARD
# ============================================================
elif page == "📊 Dashboard":
    st.markdown("<h1>📊 City Officials Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#475569;'>Analytics and insights for all civic complaints. (Demo data)</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    df = pd.DataFrame(MOCK_COMPLAINTS)

    # ---- Metrics ----
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📋 Total", len(df))
    col2.metric("✅ Resolved", len(df[df["status"] == "Resolved"]))
    col3.metric("⚙️ In Progress", len(df[df["status"] == "In Progress"]))
    col4.metric("⏳ Pending", len(df[df["status"] == "Submitted"]))

    st.markdown("---")

    # ---- Charts ----
    colA, colB = st.columns(2)

    with colA:
        st.markdown("### 📊 Complaints by Category")
        st.bar_chart(df["category"].value_counts())

    with colB:
        st.markdown("### ⚠️ Complaints by Severity")
        st.bar_chart(df["severity"].value_counts())

    st.markdown("---")

    # ---- Map ----
    st.markdown("### 🗺️ Issue Map")
    map_data = df[["latitude", "longitude"]].rename(
        columns={"latitude": "lat", "longitude": "lon"}
    )
    st.map(map_data, use_container_width=True)

    st.markdown("---")

    # ---- Table ----
    st.markdown("### 📋 All Complaints")
    st.dataframe(df, use_container_width=True, hide_index=True)
