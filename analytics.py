
import os
import pandas as pd
from sqlalchemy import create_engine

# ---------- RDS CONFIGURATION ----------
RDS_ENDPOINT = "iot-database.c5eymk6g44jl.ap-south-1.rds.amazonaws.com"
DB_USER = "admin"
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = "iotdb"
DB_PORT = 3306

if not DB_PASSWORD:
    raise ValueError("Set DB_PASSWORD in your PowerShell terminal first.")

# Connect to AWS RDS
from urllib.parse import quote_plus

password = quote_plus(DB_PASSWORD)

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{password}@{RDS_ENDPOINT}:{DB_PORT}/{DB_NAME}"
)

# 1. Total readings
query1 = """
SELECT COUNT(*) AS total_readings
FROM sensor_readings;
"""

# 2. Average temperature and humidity
query2 = """
SELECT
    ROUND(AVG(temperature), 2) AS average_temperature,
    ROUND(AVG(humidity), 2) AS average_humidity
FROM sensor_readings;
"""

# 3. Minimum and maximum temperature
query3 = """
SELECT
    MIN(temperature) AS minimum_temperature,
    MAX(temperature) AS maximum_temperature
FROM sensor_readings;
"""

# 4. Sensor-wise analytics
query4 = """
SELECT
    sensor_id,
    COUNT(*) AS total_readings,
    ROUND(AVG(temperature), 2) AS average_temperature,
    ROUND(AVG(humidity), 2) AS average_humidity
FROM sensor_readings
GROUP BY sensor_id
ORDER BY average_temperature DESC;
"""

# Execute queries and display results
queries = {
    "Total Readings": query1,
    "Average Temperature and Humidity": query2,
    "Minimum and Maximum Temperature": query3,
    "Sensor-wise Analytics": query4,
}

try:
    for title, query in queries.items():
        print(f"\n{'=' * 15} {title} {'=' * 15}")
        result = pd.read_sql(query, engine)
        print(result.to_string(index=False))
finally:
    engine.dispose()

