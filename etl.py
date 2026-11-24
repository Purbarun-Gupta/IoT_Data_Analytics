
import os
import boto3
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# ---------- AWS / S3 CONFIGURATION ----------
BUCKET_NAME = "iot-analytics-yourid-2026"
FILE_KEY = "iot_sensor_data.csv"
AWS_REGION = "ap-south-1"

# ---------- RDS CONFIGURATION ----------
RDS_ENDPOINT = "iot-database.c5eymk6g44jl.ap-south-1.rds.amazonaws.com"
DB_USER = "admin"
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = "iotdb"
DB_PORT = 3306

if not DB_PASSWORD:
    raise ValueError("Set the DB_PASSWORD environment variable first.")



# 1. Extract CSV from S3
print("Reading CSV from S3...")
s3 = boto3.client("s3", region_name=AWS_REGION)
response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
df = pd.read_csv(response["Body"])

# 2. Validate and transform
required_columns = [
    "timestamp", "sensor_id", "temperature", "humidity"
]
missing = set(required_columns) - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df = df[required_columns].copy()
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
df["humidity"] = pd.to_numeric(df["humidity"], errors="coerce")
df = df.dropna(subset=required_columns)

print(f"Valid rows to load: {len(df)}")

# 3. Connect to MySQL RDS
encoded_password = quote_plus(DB_PASSWORD)
db_url = (
    f"mysql+pymysql://{DB_USER}:{encoded_password}"
    f"@{RDS_ENDPOINT}:{DB_PORT}/{DB_NAME}"
)
engine = create_engine(db_url, pool_pre_ping=True)

# 4. Load records into RDS
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            sensor_id VARCHAR(50) NOT NULL,
            temperature FLOAT,
            humidity FLOAT
        )
    """))

df.to_sql(
    "sensor_readings",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=100
)

# 5. Verify load
with engine.connect() as conn:
    count = conn.execute(
        text("SELECT COUNT(*) FROM sensor_readings")
    ).scalar_one()

print(f"ETL completed. Total rows in sensor_readings: {count}")
engine.dispose()
