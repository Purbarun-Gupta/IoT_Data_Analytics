
import os
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="IoT Data Analytics Dashboard",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ IoT Sensor Data Analytics Dashboard")
st.caption("Live analytics from Amazon RDS MySQL")

# ---------- DATABASE CONFIGURATION ----------
RDS_ENDPOINT = (
    "iot-database.c5eymk6g44jl.ap-south-1.rds.amazonaws.com"
)
DB_USER = "admin"
DB_NAME = "iotdb"
DB_PORT = 3306
DB_PASSWORD = os.environ.get("DB_PASSWORD")

if not DB_PASSWORD:
    st.error(
        "DB_PASSWORD is not set. Set it in the terminal "
        "before launching the dashboard."
    )
    st.stop()

# ---------- CONNECT TO RDS ----------
@st.cache_resource
def get_engine():
    password = quote_plus(DB_PASSWORD)
    connection_url = (
        f"mysql+pymysql://{DB_USER}:{password}"
        f"@{RDS_ENDPOINT}:{DB_PORT}/{DB_NAME}"
    )
    return create_engine(
        connection_url,
        pool_pre_ping=True
    )

# ---------- LOAD DATA ----------
@st.cache_data(ttl=60)
def load_data():
    engine = get_engine()
    query = """
        SELECT timestamp, sensor_id, temperature, humidity
        FROM sensor_readings
        ORDER BY timestamp
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load data from RDS: {e}")
    st.stop()

if df.empty:
    st.warning("No sensor readings found in the database.")
    st.stop()

# ---------- SIDEBAR FILTER ----------
st.sidebar.header("Dashboard Filters")

sensor_options = sorted(
    df["sensor_id"].dropna().unique().tolist()
)

selected_sensors = st.sidebar.multiselect(
    "Select sensors",
    options=sensor_options,
    default=sensor_options
)

filtered_df = df[
    df["sensor_id"].isin(selected_sensors)
].copy()

if filtered_df.empty:
    st.warning("Select at least one sensor to view analytics.")
    st.stop()

if st.sidebar.button("Refresh dashboard"):
    st.cache_data.clear()
    st.rerun()


# ---------- SUMMARY METRICS ----------
st.subheader("Overview")

st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #191F2D, #121722);
    border: 1px solid #2B3548;
    border-radius: 14px;
    padding: 22px 24px;
    min-height: 145px;
    margin-bottom: 16px;
    box-shadow: 0 5px 16px rgba(0,0,0,0.16);
    transition: border-color 0.2s ease;
}

.metric-card:hover {
    border-color: #536782;
}

.metric-accent {
    height: 3px;
    border-radius: 3px;
    margin: -22px -24px 19px -24px;
}

.metric-heading {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #B8C2D4;
    font-size: 19px;
    font-weight: 600;
    margin-bottom: 17px;
}

.metric-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
}

.metric-value {
    color: #F4F7FC;
    font-size: 40px;
    font-weight: 700;
    line-height: 1.2;
    letter-spacing: -0.5px;
}

/* Make sensor summary table text larger */
div[data-testid="stDataFrame"] [data-testid="glideDataEditor"] {
    font-size: 22px !important;
}

</style>
""", unsafe_allow_html=True)

total_readings = len(filtered_df)
avg_temperature = filtered_df["temperature"].mean()
avg_humidity = filtered_df["humidity"].mean()
sensors_count = filtered_df["sensor_id"].nunique()

# First row
col1, col2 = st.columns(2, gap="small")

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-accent" style="background:#60A5FA;"></div>
        <div class="metric-heading">
            <div class="metric-icon" style="background:#203754;">📊</div>
            Total Readings
        </div>
        <div class="metric-value">{total_readings:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-accent" style="background:#FB923C;"></div>
        <div class="metric-heading">
            <div class="metric-icon" style="background:#493021;">🌡️</div>
            Average Temperature
        </div>
        <div class="metric-value">
            {avg_temperature:.2f}
            <span style="font-size:20px;color:#FB923C;">°C</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Second row
col3, col4 = st.columns(2, gap="small")

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-accent" style="background:#22D3EE;"></div>
        <div class="metric-heading">
            <div class="metric-icon" style="background:#153B46;">💧</div>
            Average Humidity
        </div>
        <div class="metric-value">
            {avg_humidity:.2f}
            <span style="font-size:20px;color:#22D3EE;">%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-accent" style="background:#A78BFA;"></div>
        <div class="metric-heading">
            <div class="metric-icon" style="background:#322849;">📡</div>
            Sensors Selected
        </div>
        <div class="metric-value">{sensors_count}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()


# ---------- TIME SERIES CHARTS ----------
st.markdown(
    "<h2 style='font-size:36px; font-weight:700;'>"
    "Sensor Trends</h2>",
    unsafe_allow_html=True
)

temperature_fig = px.line(
    filtered_df,
    x="timestamp",
    y="temperature",
    color="sensor_id",
    markers=True,
    title="Temperature Over Time",
    labels={
        "timestamp": "Timestamp",
        "temperature": "Temperature (°C)",
        "sensor_id": "Sensor"
    }
)

temperature_fig.update_layout(
    height=450,
    title_font=dict(size=26),
    font=dict(size=15),
    xaxis_title_font=dict(size=17),
    yaxis_title_font=dict(size=17),
    legend=dict(font=dict(size=14))
)

st.plotly_chart(
    temperature_fig,
    use_container_width=True
)

humidity_fig = px.line(
    filtered_df,
    x="timestamp",
    y="humidity",
    color="sensor_id",
    markers=True,
    title="Humidity Over Time",
    labels={
        "timestamp": "Timestamp",
        "humidity": "Humidity (%)",
        "sensor_id": "Sensor"
    }
)

humidity_fig.update_layout(
    height=450,
    title_font=dict(size=26),
    font=dict(size=15),
    xaxis_title_font=dict(size=17),
    yaxis_title_font=dict(size=17),
    legend=dict(font=dict(size=14))
)

st.plotly_chart(
    humidity_fig,
    use_container_width=True
)

# ---------- SENSOR COMPARISON ----------
st.subheader("Sensor Comparison")

sensor_summary = (
    filtered_df.groupby("sensor_id")
    .agg(
        readings=("temperature", "count"),
        avg_temperature=("temperature", "mean"),
        avg_humidity=("humidity", "mean"),
        min_temperature=("temperature", "min"),
        max_temperature=("temperature", "max")
    )
    .reset_index()
)

sensor_summary = sensor_summary.round(2)

comparison_fig = px.bar(
    sensor_summary,
    x="sensor_id",
    y="avg_temperature",
    color="sensor_id",
    title="Average Temperature by Sensor",
    labels={
        "sensor_id": "Sensor",
        "avg_temperature": "Average Temperature (°C)"
    },
    text_auto=".2f"
)


comparison_fig.update_layout(
    title_font=dict(size=30),
    font=dict(size=40),
    xaxis=dict(
        title_font=dict(size=15),
        tickfont=dict(size=18)
    ),
    yaxis=dict(
        title_font=dict(size=15),
        tickfont=dict(size=18)
    ),
    legend=dict(
        title_font=dict(size=15),
        font=dict(size=17)
    )
)

comparison_fig.update_traces(
    textfont=dict(size=18)
)


st.plotly_chart(
    comparison_fig,
    use_container_width=True
)


# ---------- SENSOR SUMMARY TABLE ----------
st.markdown(
    "<h2 style='font-size:30px; font-weight:700;'>"
    "📋 Sensor Summary</h2>",
    unsafe_allow_html=True
)


st.dataframe(
    sensor_summary,
    use_container_width=True,
    hide_index=True,
    height=160,
    row_height=42,
    column_config={
        "sensor_id": st.column_config.TextColumn(
            "Sensor ID",
            width="medium"
        ),
        "readings": st.column_config.NumberColumn(
            "Readings",
            width="small",
            format="%d"
        ),
        "avg_temperature": st.column_config.NumberColumn(
            "Average Temperature (°C)",
            width="medium",
            format="%.2f"
        ),
        "avg_humidity": st.column_config.NumberColumn(
            "Average Humidity (%)",
            width="medium",
            format="%.2f"
        ),
        "min_temperature": st.column_config.NumberColumn(
            "Minimum Temperature (°C)",
            width="medium",
            format="%.2f"
        ),
        "max_temperature": st.column_config.NumberColumn(
            "Maximum Temperature (°C)",
            width="medium",
            format="%.2f"
        )
    }
)


# ---------- RAW DATA ----------
with st.expander("🔎 Explore All Sensor Readings"):
    st.caption(
        f"Showing {len(filtered_df):,} readings "
        "for the selected sensors."
    )
    st.dataframe(
        filtered_df.sort_values(
            "timestamp", ascending=False
        ),
        use_container_width=True,
        hide_index=True,
        height=400
    )

# ---------- DOWNLOAD ----------
st.markdown(
    "<h2 style='font-size:30px; font-weight:700;'>"
    "📥 Export Your Data</h2>",
    unsafe_allow_html=True
)

st.caption(
    "Download the readings currently selected "
    "by your sensor filters."
)

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Data (CSV)",
    data=csv_data,
    file_name="filtered_iot_sensor_data.csv",
    mime="text/csv"
)

st.caption(
    "🌡️ Data pipeline: Amazon S3 → Python ETL → "
    "Amazon RDS MySQL"
)


