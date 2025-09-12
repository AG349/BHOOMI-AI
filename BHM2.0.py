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

# -------------------- RISK GAUGE --------------------
st.subheader("🧭 Risk Gauge")
gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=current_risk,
    title={"text":"Current Risk %"},
    gauge={
        "axis":{"range":[0,100]},
        "bar":{"color":"cyan"},
        "steps":[
            {"range":[0,40],"color":"green"},
            {"range":[40,70],"color":"yellow"},
            {"range":[70,100],"color":"red"}
        ]
    }
))
gauge.update_layout(paper_bgcolor="#0d1117", font={"color":"#00FFEF"})
st.plotly_chart(gauge, use_container_width=True)

# -------------------- VIBRATION + SLOPE --------------------
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📈 Vibration Trend")
    fig_vibration = px.line(df, x="Timestamp", y="Vibration", markers=True,
                            title="Vibration Levels", line_shape="spline",
                            color_discrete_sequence=["orange"])
    fig_vibration.update_layout(template="plotly_dark",
                                plot_bgcolor="#0d1117", paper_bgcolor="#0d1117")
    st.plotly_chart(fig_vibration, use_container_width=True)

with col_b:
    st.subheader("⛰ Slope Angle Trend")
    fig_slope = px.line(df, x="Timestamp", y="Slope", markers=True,
                        title="Slope Angle", line_shape="spline",
                        color_discrete_sequence=["lime"])
    fig_slope.update_layout(template="plotly_dark",
                            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117")
    st.plotly_chart(fig_slope, use_container_width=True)

# -------------------- THERMAL HEATMAP --------------------
st.subheader("🌡 Thermal Heatmap with Sensor Hotspots")

heat_data = np.random.normal(loc=current_risk, scale=15, size=(20, 20))
heat_data = np.clip(heat_data, 0, 100)

heat_fig = px.imshow(
    heat_data,
    color_continuous_scale="plasma",
    origin="lower",
    aspect="auto",
    labels=dict(color="Temperature / Risk Level"),
    title="Thermal Activity Heatmap",
    zmin=0, zmax=100
)

sensor_x = np.random.randint(0, 20, 6)
sensor_y = np.random.randint(0, 20, 6)
heat_fig.add_trace(go.Scatter(
    x=sensor_x, y=sensor_y,
    mode="markers+text",
    marker=dict(size=12, color="white", symbol="x"),
    text=[f"Sensor {i+1}" for i in range(6)],
    textposition="top center"
))

heat_fig.update_layout(template="plotly_dark", plot_bgcolor="#0d1117", paper_bgcolor="#0d1117")
st.plotly_chart(heat_fig, use_container_width=True)

# -------------------- ALERTS LOG --------------------
st.subheader("🚨 Alerts Log")
alerts = df.tail(5).copy()
alerts["Action"] = np.where(alerts["Risk"]>70,"🔴 Evacuation",
                     np.where(alerts["Risk"]>40,"🟡 Warning","🟢 Monitoring"))
st.dataframe(alerts, use_container_width=True)

# -------------------- RESTRICTED AREA ALERT --------------------
st.subheader("🚫 Restricted Area Detection")
restricted_areas = ["Zone A", "Zone C", "Zone E"]
worker_zones = np.random.choice(["Zone A","Zone B","Zone C","Zone D","Zone E"], size=5)
restricted_alerts = [zone for zone in worker_zones if zone in restricted_areas]

if restricted_alerts:
    st.warning(f"⚠ Restricted Area Alert! Workers detected in: {', '.join(restricted_alerts)}")
    alerts.loc[len(alerts)] = {
        "Timestamp": datetime.now().strftime("%H:%M:%S"),
        "Vibration": np.nan,
        "Slope": np.nan,
        "Weather": np.nan,
        "Risk": 100,
        "Action": "🚫 Restricted Area Entry"
    }
else:
    st.info("✅ No workers in restricted areas.")

# -------------------- WORKER GEO-LOCATION --------------------
st.subheader("📍 Worker Location Tracking (Geo Map)")

mine_center = {"lat": 20.5937, "lon": 78.9629}  # Example central point

num_workers = 10
worker_positions = pd.DataFrame({
    "Worker": [f"Worker {i+1}" for i in range(num_workers)],
    "lat": mine_center["lat"] + np.random.uniform(-0.01, 0.01, num_workers),
    "lon": mine_center["lon"] + np.random.uniform(-0.01, 0.01, num_workers)
})

restricted_zone = {"lat": mine_center["lat"] + 0.005,
                   "lon": mine_center["lon"] - 0.005,
                   "radius_km": 0.7}

fig_workers = px.scatter_mapbox(
    worker_positions, lat="lat", lon="lon", text="Worker",
    zoom=14, height=600, color_discrete_sequence=["cyan"]
)

fig_workers.add_trace(go.Scattermapbox(
    lat=[restricted_zone["lat"]],
    lon=[restricted_zone["lon"]],
    mode="markers+text",
    marker=dict(size=18, color="red"),
    text=["🚫 Restricted Zone"],
    textposition="top right"
))

fig_workers.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor="#0d1117",
    font=dict(color="white")
)

st.plotly_chart(fig_workers, use_container_width=True)

# -------------------- MANUAL ALERT --------------------
st.subheader("📢 Trigger Manual Alert")
if st.button("🚨 SEND ALERT NOW"):
    st.success("✅ Alert sent to all registered numbers! (Simulated in demo mode)")

# -------------------- FORECAST --------------------
st.subheader("🔮 Forecast (Next 6 Hours)")
hours = [f"{i}h" for i in range(1,7)]
forecast = np.random.randint(20,95,size=6)
df_forecast = pd.DataFrame({"Hour":hours,"Forecast Risk %":forecast})
fig_forecast = px.bar(df_forecast, x="Hour", y="Forecast Risk %",
                      color="Forecast Risk %", title="Predicted Risk Probability",
                      color_continuous_scale="turbo")
fig_forecast.update_layout(template="plotly_dark", plot_bgcolor="#0d1117", paper_bgcolor="#0d1117")
st.plotly_chart(fig_forecast, use_container_width=True)

# -------------------- RESTRICTED AREA ALERT WITH WORKER ALERT BUTTON --------------------
st.subheader("🚫 Restricted Area Detection")
restricted_areas = ["Zone A", "Zone C", "Zone E"]
worker_zones = np.random.choice(["Zone A","Zone B","Zone C","Zone D","Zone E"], size=5)
restricted_alerts = [zone for zone in worker_zones if zone in restricted_areas]

if restricted_alerts:
    st.warning(f"⚠ Restricted Area Alert! Workers detected in: {', '.join(restricted_alerts)}")
    alerts.loc[len(alerts)] = {
        "Timestamp": datetime.now().strftime("%H:%M:%S"),
        "Vibration": np.nan,
        "Slope": np.nan,
        "Weather": np.nan,
        "Risk": 100,
        "Action": "🚫 Restricted Area Entry"
    }
else:
    st.info("✅ No workers in restricted areas.")

# Button to alert workers near restricted zone
if st.button("📢 Alert Workers Near Restricted Area"):
    if restricted_alerts:
        st.success(f"✅ Alert sent to workers in restricted zones: {', '.join(restricted_alerts)}")
    else:
        st.info("ℹ No workers currently near restricted areas to alert.")

# -------------------- AUTO REFRESH --------------------
st_autorefresh(interval=60*1000, key="auto_refresh")

# -------------------- FOOTER --------------------
st.markdown("---")
st.markdown("🧠 BHOOMI Safety Core v3.1 | Live + CSV + Alerts + Forecast + Heatmap + GeoMap | TEAM BHOOMI ⚡")
