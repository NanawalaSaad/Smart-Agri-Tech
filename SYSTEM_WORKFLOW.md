# Smart Agri-Tech Workflow

```text
+--------------------+
|   Environmental    |
|      Sensors       |
+---------+----------+
          |
          v
+--------------------+
|      ESP32 MCU     |
| Sensor Collection  |
+---------+----------+
          |
     HTTP POST
          |
          v
+--------------------+
|    Flask Backend   |
|      (API)         |
+---------+----------+
          |
          v
+--------------------+
| Expert System / AI |
| Crop Recommendation|
+---------+----------+
          |
          +----------------------+
          |                      |
          v                      v
+----------------+      +------------------+
| Care Schedule  |      | Yield Prediction |
+----------------+      +------------------+
          |
          v
+--------------------+
|  Web Dashboard     |
| HTML/CSS/JS        |
+--------------------+
```

## Workflow

1. Sensors continuously collect environmental data.
2. ESP32 reads all sensor values.
3. Data is sent via HTTP POST request.
4. Flask API receives and validates the data.
5. Expert System compares values with crop database.
6. Best crop recommendation is generated.
7. Watering, fertilizer and sunlight schedules are created.
8. Results are displayed on the dashboard.