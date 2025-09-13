import streamlit as st 
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="BHOOMI Rockfall AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    body { background-color: #0d1117; color: #00FFEF; }
    .stMetric { background: rgba(0, 255, 239, 0.1);
                border-radius: 15px; padding: 10px; border: 1px solid #00FFEF; }
    .stDataFrame { border: 1px solid #00FFEF; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 BHOOMI Safety Interface")
st.markdown("### AI-Powered Rockfall Prediction & Alert System")
st.markdown("System Status: 🔵 Online | Mode: Multimodal Fusion Active")
st.divider()

# -------------------- DATA SOURCE --------------------
mode = st.radio("📊 Select Data Source:", ["Simulated Live Data", "Preloaded CSV", "Upload CSV"])

if mode == "Preloaded CSV":
    try:
        df = pd.read_csv("mine_sensor_data.csv")
        st.success("✅ Preloaded CSV loaded successfully!")
    except:
        st.error("⚠ Preloaded file 'mine_sensor_data.csv' not found.")
        st.stop()

elif mode == "Upload CSV":
    uploaded = st.file_uploader("📂 Upload your CSV file", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.success("✅ Uploaded CSV loaded successfully!")
    else:
        st.warning("Please upload a CSV to continue.")
        st.stop()

else:
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(columns=["Timestamp","Vibration","Slope","Weather","Risk"])
    new_data = {
        "Timestamp": datetime.now().strftime("%H:%M:%S"),
        "Vibration": round(np.random.normal(0.5,0.2),3),
        "Slope": round(np.random.normal(45,3),2),
        "Weather": np.random.choice(["Sunny","Rainy","Cloudy","Windy"]),
        "Risk": np.random.randint(0,100)
    }
    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_data])], ignore_index=True)
    df = st.session_state.df.tail(50)

# -------------------- METRICS --------------------
col1, col2, col3, col4 = st.columns(4)
current_risk = df["Risk"].iloc[-1]
if current_risk > 70:
    risk_status = "🔴 HIGH"
elif current_risk > 40:
    risk_status = "🟡 MEDIUM"
else:
    risk_status = "🟢 LOW"

with col1: st.metric("Current Risk", risk_status)
with col2: st.metric("Active Sensors", "📸 5 | 🎙 3")
with col3: st.metric("Last Update", str(df["Timestamp"].iloc[-1]))
with col4: st.metric("Weather", df["Weather"].iloc[-1])

st.divider()

# -------------------- DYNAMIC RISK GAUGE --------------------
st.subheader("🧭 Risk Gauge")

gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=current_risk,
    title={"text": "Current Risk %"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "cyan"},
        "steps": [
            {"range": [0, 40], "color": "green"},   # Low
            {"range": [40, 70], "color": "yellow"}, # Medium
            {"range": [70, 100], "color": "red"}    # High
        ]
    }
))

gauge.update_layout(
    paper_bgcolor="#0d1117",
    font={"color": "#00FFEF"}
)

st.plotly_chart(gauge, use_container_width=True)

# -------------------- VIBRATION + SLOPE --------------------
col_a, col_b = st.columns(2)

# --- Vibration ---
vib_min, vib_max = df["Vibration"].min(), df["Vibration"].max()
vib_range = vib_max - vib_min
vib_low = vib_min + 0.3 * vib_range
vib_high = vib_min + 0.7 * vib_range

with col_a:
    st.subheader("📈 Vibration Trend")
    fig_vibration = px.line(df, x="Timestamp", y="Vibration", markers=True,
                            title="Vibration Levels", line_shape="spline",
                            color_discrete_sequence=["orange"])
    fig_vibration.update_layout(template="plotly_dark",
                                plot_bgcolor="#0d1117", paper_bgcolor="#0d1117")
    fig_vibration.add_hrect(y0=vib_min, y1=vib_low, fillcolor="green", opacity=0.2, line_width=0, annotation_text="Low", annotation_position="left")
    fig_vibration.add_hrect(y0=vib_high, y1=vib_max, fillcolor="red", opacity=0.2, line_width=0, annotation_text="High", annotation_position="left")
    st.plotly_chart(fig_vibration, use_container_width=True)

# --- Slope ---
slope_min, slope_max = df["Slope"].min(), df["Slope"].max()
slope_range = slope_max - slope_min
slope_low = slope_min + 0.3 * slope_range
slope_high = slope_min + 0.7 * slope_range

with col_b:
    st.subheader("⛰ Slope Angle Trend")
    fig_slope = px.line(df, x="Timestamp", y="Slope", markers=True,
                        title="Slope Angle", line_shape="spline",
                        color_discrete_sequence=["lime"])
    fig_slope.update_layout(template="plotly_dark",
                            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117")
    fig_slope.add_hrect(y0=slope_min, y1=slope_low, fillcolor="green", opacity=0.2, line_width=0, annotation_text="Low", annotation_position="left")
    fig_slope.add_hrect(y0=slope_high, y1=slope_max, fillcolor="red", opacity=0.2, line_width=0, annotation_text="High", annotation_position="left")
    st.plotly_chart(fig_slope, use_container_width=True)

# -------------------- THERMAL HEATMAP WITH AXES + SENSORS --------------------
st.subheader("🌡 Thermal Heatmap with Sensors (X=100, Y=40)")

# Heatmap data with Y=100 rows, X=40 columns
heat_data = np.random.normal(loc=current_risk, scale=15, size=(40, 100))
heat_data = np.clip(heat_data, 0, 100)

# Sensor positions (X=0–40, Y=0–100)
sensors = {
    "S1": (5, 90),
    "S2": (10, 70),
    "S3": (25, 30),
    "S4": (35, 85),
    "S5": (15, 50),
    "S6": (30, 20),
}

heat_fig = go.Figure(data=go.Heatmap(
    z=heat_data,
    colorscale="Viridis",
    zmin=0, zmax=100,
    colorbar=dict(
        title="Risk Level",
        tickvals=[0, 50, 100],
        ticktext=["Low", "Medium", "High"]
    )
))

# Add sensors
for name, (x, y) in sensors.items():
    heat_fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode="markers+text",
        marker=dict(size=12, color="white", symbol="x"),
        text=[name],
        textposition="top center",
        showlegend=False
    ))

# ✅ Axes X: 0–40, Y: 0–100
heat_fig.update_layout(
    title="Thermal Activity Heatmap",
    template="plotly_dark",
    plot_bgcolor="#0d1117",
    paper_bgcolor="#0d1117",
    xaxis=dict(title="X Axis", range=[0, 40], showgrid=False, zeroline=False),
    yaxis=dict(title="Y Axis", range=[0, 100], showgrid=False, zeroline=False),
    height=600
)

st.plotly_chart(heat_fig, use_container_width=True)

# -------------------- ALERTS LOG --------------------
st.subheader("🚨 Alerts Log")
alerts = df.tail(5).copy()
alerts["Action"] = np.where(alerts["Risk"]>70,"🔴 Evacuation",
                     np.where(alerts["Risk"]>40,"🟡 Warning","🟢 Monitoring"))
st.dataframe(alerts, use_container_width=True)

# -------------------- AUTO REFRESH --------------------
st_autorefresh(interval=60*1000, key="auto_refresh")

# -------------------- FOOTER --------------------
st.markdown("---")
st.markdown("🧠 BHOOMI Safety Core v3.2 | Live + CSV + Alerts + Forecast + Heatmap (X/Y Axis) | TEAM BHOOMI ⚡")
