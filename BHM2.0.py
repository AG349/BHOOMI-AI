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

else:  # Simulated Live Data
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(columns=["Timestamp", "Vibration", "Slope", "Weather", "Risk"])
    new_data = {
        "Timestamp": datetime.now().strftime("%H:%M:%S"),
        "Vibration": round(np.random.normal(0.5, 0.2), 3),
        "Slope": round(np.random.normal(45, 3), 2),
        "Weather": np.random.choice(["Sunny", "Rainy", "Cloudy", "Windy"]),
        "Risk": np.random.randint(0, 100)
    }
    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_data])], ignore_index=True)
    df = st.session_state.df.tail(50)

# -------------------- FUNCTIONS --------------------
def risk_gauge(value):
    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": "Current Risk %"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "cyan"},
            "steps": [
                {"range": [0, 30], "color": "green"},
                {"range": [30, 70], "color": "yellow"},
                {"range": [70, 100], "color": "red"}
            ]
        }
    ))
    gauge.update_layout(paper_bgcolor="#0d1117", font={"color": "#00FFEF"})
    return gauge

def trend_chart(df, column, title, color, low, high):
    fig = px.line(df, x="Timestamp", y=column, markers=True,
                  title=title, line_shape="spline",
                  color_discrete_sequence=[color])
    fig.update_layout(template="plotly_dark",
                      plot_bgcolor="#0d1117", paper_bgcolor="#0d1117")
    fig.add_hrect(y0=df[column].min(), y1=low, fillcolor="green", opacity=0.2,
                  line_width=0, annotation_text="Low", annotation_position="left")
    fig.add_hrect(y0=high, y1=df[column].max(), fillcolor="red", opacity=0.2,
                  line_width=0, annotation_text="High", annotation_position="left")
    return fig

def thermal_heatmap(current_risk):
    heat_data = np.random.normal(loc=current_risk, scale=15, size=(100, 100))
    heat_data = np.clip(heat_data, 0, 100)
    fig = px.imshow(
        heat_data,
        color_continuous_scale="plasma",
        origin="lower",
        aspect="auto",
        labels=dict(color="Temperature / Risk Level"),
        title="Thermal Activity Heatmap",
        zmin=0, zmax=100
    )
    # Add sensor points
    sensor_x = np.random.randint(0, 100, 6)
    sensor_y = np.random.randint(0, 100, 6)
    fig.add_trace(go.Scatter(
        x=sensor_x, y=sensor_y,
        mode="markers+text",
        marker=dict(size=12, color="white", symbol="x"),
        text=[f"Sensor {i+1}" for i in range(6)],
        textposition="top center"
    ))
    # Risk labels
    fig.add_annotation(x=102, y=np.percentile(heat_data, 30), text="Low Risk",
                       showarrow=False, font=dict(color="green", size=12))
    fig.add_annotation(x=102, y=np.percentile(heat_data, 70), text="High Risk",
                       showarrow=False, font=dict(color="red", size=12))
    fig.update_layout(template="plotly_dark", plot_bgcolor="#0d1117",
                      paper_bgcolor="#0d1117", xaxis=dict(range=[0, 100]),
                      yaxis=dict(range=[0, 100]), margin=dict(r=80))
    return fig

def forecast_chart():
    hours = [f"{i}h" for i in range(1, 7)]
    forecast = np.random.randint(20, 95, size=6)
    df_forecast = pd.DataFrame({"Hour": hours, "Forecast Risk %": forecast})
    fig = px.bar(df_forecast, x="Hour", y="Forecast Risk %",
                 color="Forecast Risk %", title="Predicted Risk Probability",
                 color_continuous_scale="turbo")
    fig.update_layout(template="plotly_dark", plot_bgcolor="#0d1117", paper_bgcolor="#0d1117")
    return fig

def worker_map():
    mine_center = {"lat": 20.5937, "lon": 78.9629}
    num_workers = 10
    worker_positions = pd.DataFrame({
        "Worker": [f"Worker {i+1}" for i in range(num_workers)],
        "lat": mine_center["lat"] + np.random.uniform(-0.01, 0.01, num_workers),
        "lon": mine_center["lon"] + np.random.uniform(-0.01, 0.01, num_workers)
    })
    restricted_zone = {"lat": mine_center["lat"] + 0.005,
                       "lon": mine_center["lon"] - 0.005,
                       "radius_km": 0.7}
    fig = px.scatter_mapbox(worker_positions, lat="lat", lon="lon", text="Worker",
                            zoom=14, height=600, color_discrete_sequence=["cyan"])
    fig.add_trace(go.Scattermapbox(
        lat=[restricted_zone["lat"]],
        lon=[restricted_zone["lon"]],
        mode="markers+text",
        marker=dict(size=18, color="red"),
        text=["🚫 Restricted Zone"],
        textposition="top right",
        textfont=dict(color="black")
    ))
    fig.update_layout(mapbox_style="open-street-map",
                      margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      paper_bgcolor="#0d1117", font=dict(color="black"))
    return fig

# -------------------- METRICS --------------------
col1, col2, col3, col4 = st.columns(4)
current_risk = df["Risk"].iloc[-1]
risk_status = "🔴 HIGH" if current_risk > 70 else "🟡 MEDIUM" if current_risk > 40 else "🟢 LOW"

with col1: st.metric("Current Risk", risk_status)
with col2: st.metric("Active Sensors", "📸 5 | 🎙 3")
with col3: st.metric("Last Update", str(df["Timestamp"].iloc[-1]))
with col4: st.metric("Weather", df["Weather"].iloc[-1])

st.divider()

# -------------------- DASHBOARD --------------------
st.subheader("🧭 Risk Gauge")
st.plotly_chart(risk_gauge(current_risk), use_container_width=True)

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("📈 Vibration Trend")
    st.plotly_chart(trend_chart(df, "Vibration", "Vibration Levels", "orange",
                                df["Vibration"].quantile(0.3),
                                df["Vibration"].quantile(0.7)), use_container_width=True)

with col_b:
    st.subheader("⛰ Slope Angle Trend")
    st.plotly_chart(trend_chart(df, "Slope", "Slope Angle", "lime",
                                df["Slope"].quantile(0.3),
                                df["Slope"].quantile(0.7)), use_container_width=True)

st.subheader("🌡 Thermal Heatmap with Sensor Hotspots")
st.plotly_chart(thermal_heatmap(current_risk), use_container_width=True)

st.subheader("🚨 Alerts Log")
alerts = df.tail(5).copy()
alerts["Action"] = np.where(alerts["Risk"] > 70, "🔴 Evacuation",
                     np.where(alerts["Risk"] > 40, "🟡 Warning", "🟢 Monitoring"))
st.dataframe(alerts, use_container_width=True)

st.subheader("🚫 Restricted Area Detection")
restricted_areas = ["Zone A", "Zone C", "Zone E"]
worker_zones = np.random.choice(["Zone A", "Zone B", "Zone C", "Zone D", "Zone E"], size=5)
restricted_alerts = [zone for zone in worker_zones if zone in restricted_areas]

if restricted_alerts:
    st.warning(f"⚠ Restricted Area Alert! Workers detected in: {', '.join(restricted_alerts)}")
else:
    st.info("✅ No workers in restricted areas.")

st.plotly_chart(worker_map(), use_container_width=True)

if st.button("📢 Alert Workers Near Restricted Area"):
    if restricted_alerts:
        st.success(f"✅ Alert sent to workers in restricted zones: {', '.join(restricted_alerts)}")
    else:
        st.info("ℹ No workers currently near restricted areas to alert.")

st.subheader("📢 Trigger Manual Alert")
if st.button("🚨 SEND ALERT NOW"):
    st.success("✅ Alert sent to all registered numbers! (Simulated in demo mode)")

st.subheader("🔮 Forecast (Next 6 Hours)")
st.plotly_chart(forecast_chart(), use_container_width=True)

# -------------------- AUTO REFRESH --------------------
st_autorefresh(interval=60 * 1000, key="auto_refresh")

# -------------------- FOOTER --------------------
st.markdown("---")
st.markdown("🧠 BHOOMI Safety Core v3.2 | Modular Dashboard | TEAM BHOOMI ⚡")
