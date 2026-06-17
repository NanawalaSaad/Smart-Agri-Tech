import requests

data = {
    "temperature": 42,
    "humidity": 25,
    "soil_moisture": 60,
    "pH_level": 6.5,
    "light_hours": 12,
    "water_given_ml": 300,
    "nutrient_level": 80,
    "co2_ppm": 800,
    "day_number": 45,
    "heat_stress_index": 31.5,
    "water_efficiency": 4.9,
    "pH_deviation": 0.0,
    "growth_score": 9.6
}

response = requests.post(
    "http://127.0.0.1:5000/predict",
    json=data
)

print(response.json())
