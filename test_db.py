
import os
import pymysql

# ---------- RDS CONFIGURATION ----------
RDS_ENDPOINT = "iot-database.c5eymk6g44jl.ap-south-1.rds.amazonaws.com"
DB_USER = "admin"
DB_PORT = 3306

connection = None

try:
    # Connect to the built-in MySQL database
    connection = pymysql.connect(
        host=RDS_ENDPOINT,
        user=DB_USER,
        password=os.environ["DB_PASSWORD"],
        port=DB_PORT,
        connect_timeout=10,
        database="mysql"
    )

    with connection.cursor() as cursor:
        # Verify the MySQL connection
        cursor.execute("SELECT VERSION()")
        print("Connected to MySQL successfully!")
        print("MySQL version:", cursor.fetchone()[0])

        # Create the project database if it doesn't exist
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS iotdb"
        )

    print("Database iotdb is ready!")

except Exception as e:
    print("Database setup failed:", e)

finally:
    if connection:
        connection.close()

