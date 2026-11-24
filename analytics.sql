```sql
USE iotdb;

-- 1. Total number of readings
SELECT COUNT(*) AS total_readings
FROM sensor_readings;

-- 2. Average temperature and humidity
SELECT
    ROUND(AVG(temperature), 2) AS average_temperature,
    ROUND(AVG(humidity), 2) AS average_humidity
FROM sensor_readings;

-- 3. Minimum and maximum temperature
SELECT
    MIN(temperature) AS minimum_temperature,
    MAX(temperature) AS maximum_temperature
FROM sensor_readings;

-- 4. Readings and averages for each sensor
SELECT
    sensor_id,
    COUNT(*) AS total_readings,
    ROUND(AVG(temperature), 2) AS average_temperature,
    ROUND(AVG(humidity), 2) AS average_humidity
FROM sensor_readings
GROUP BY sensor_id
ORDER BY average_temperature DESC;

-- 5. Highest-temperature readings
SELECT *
FROM sensor_readings
ORDER BY temperature DESC
LIMIT 10;
```