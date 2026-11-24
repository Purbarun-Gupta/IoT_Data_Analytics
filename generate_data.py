
import csv
import random
from datetime import datetime, timedelta

random.seed(42)

filename = "iot_sensor_data.csv"

sensor_ids = ["SENSOR_01", "SENSOR_02", "SENSOR_03"]
start_time = datetime(2026, 10, 1, 8, 0, 0)

with open(filename, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "timestamp",
        "sensor_id",
        "temperature",
        "humidity"
    ])

    for i in range(300):
        timestamp = start_time + timedelta(minutes=10 * i)
        sensor_id = sensor_ids[i % len(sensor_ids)]

        temperature = round(random.uniform(20, 38), 2)
        humidity = round(random.uniform(30, 85), 2)

        writer.writerow([
            timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            sensor_id,
            temperature,
            humidity
        ])

print(f"Dataset created: {filename}")
print("Total sensor readings: 300")
