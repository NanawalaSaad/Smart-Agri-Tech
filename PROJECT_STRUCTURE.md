# Smart Agri-Tech Project Structure

```
Smart-Agri-Tech
│
├── IoT/
│   └── ESP32 firmware and sensor integration
│
├── API/
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│       ├── index.html
│       ├── crop.html
│       ├── hardware.html
│       ├── insights.html
│       ├── schedule.html
│       ├── sensors.html
│       ├── playbook.html
│       ├── protection.html
│       ├── predict_options.html
│       ├── contact.html
│       └── about pages
│
├── dashboard/
│   └── Streamlit dashboard
│
│
│
├── data/
│   └── processed/
│        ├── desert_crops_250.csv
│
│
│
├── models/
│   ├── crop_recommender_model.pkl
│   └── expert_system_db.pkl
│
├── notebooks/
│   ├── 00_dataset_generation.ipynb
│   ├── 01_eda.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_ml_model.ipynb
│   └── 04_crop_recommendation.ipynb
│
├── screenshots/
│
├── README.md
│
└── .gitignore
```

## Workflow

1. ESP32 reads live sensors.
2. Sensor values are transmitted using HTTP POST.
3. Flask backend receives telemetry.
4. AI Expert System processes environmental parameters.
5. Best crop is selected.
6. Watering, fertilizer and sunlight schedules are generated.
7. Results are displayed on the web dashboard.