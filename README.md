# 🌾 Smart Desert Agri-Tech

<div align="center">

### AI + IoT Based Smart Agriculture System for Desert & Resource-Constrained Environments

**Built with ESP32 • Flask • Python • Expert System • IoT • Render Cloud**

</div>

---

## 📖 Overview

Smart Desert Agri-Tech is an AI and IoT powered precision agriculture platform designed specifically for hyper-arid and desert environments.

The system combines real-time environmental sensing using ESP32 hardware with an intelligent expert recommendation engine to assist farmers in crop selection, irrigation planning, yield estimation and environmental monitoring.

Unlike traditional smart farming systems, this project focuses on desert agriculture where water availability, alkaline soil and extreme temperatures make cultivation challenging.

---

# 🎯 Problem Statement

Desert agriculture faces multiple challenges including:

- Water scarcity
- High temperature
- Low humidity
- Soil alkalinity
- Crop selection difficulties
- Resource wastage

This project provides an intelligent decision support system capable of monitoring field conditions in real time and recommending suitable crops together with irrigation schedules.

---

# ✨ Features

- 🌡️ Real-Time Temperature Monitoring
- 💧 Live Humidity Monitoring
- 🌱 Soil Moisture Monitoring
- ⚗️ Soil pH Analysis
- ☀️ Light Exposure Monitoring
- 🌧️ Rain Detection
- 📏 Reservoir Water Level Monitoring
- 🤖 AI Crop Recommendation
- 🌾 Yield Prediction
- 📅 Smart Crop Timeline Prediction
- 💦 Smart Watering Schedule
- 🌿 Fertilizer Recommendation
- ☁️ Cloud Dashboard
- 📡 ESP32 Live Sensor Integration
- 🧠 Expert System Based Decision Engine

---

# 🏗️ System Architecture

```
Environmental Sensors
        │
        ▼
      ESP32
        │
        ▼
 HTTP POST Requests
        │
        ▼
 Flask Backend Server
        │
 ┌──────┼─────────────┐
 │      │             │
 ▼      ▼             ▼
AI Engine Dashboard Prediction
 │
 ▼
Crop Recommendation
 │
 ▼
Smart Irrigation Schedule
 │
 ▼
Farmer Dashboard
```

---

# ⚙️ Hardware Components

- ESP32 Development Board
- Temperature Sensor
- Humidity Sensor
- Soil Moisture Sensor
- pH Sensor
- Rain Sensor
- LDR Sensor
- Ultrasonic Sensor

---

# 💻 Software Stack

### Backend

- Python
- Flask
- Flask-CORS
- Gunicorn

### Frontend

- HTML5
- CSS3
- JavaScript

### AI & Data

- Expert System
- Pickle Database
- Jupyter Notebook

### IoT

- ESP32
- Arduino IDE

### Deployment

- GitHub
- Render Cloud

---

# 🧠 AI Prediction Engine

The prediction engine evaluates live sensor data using a weighted expert system.

Parameters include:

- Temperature
- Humidity
- Soil Moisture
- Soil pH

Each crop receives a weighted score.

The system then calculates:

- Crop suitability
- Estimated yield
- Growth timeline
- Watering schedule
- Fertilizer recommendation

---

# 📊 Dashboard Modules

- Live Sensor Dashboard
- AI Prediction Hub
- Crop Recommendation
- Hardware Monitoring
- Smart Schedule
- Insights
- Protection Module
- AI Playbook

---

# 📂 Project Structure

```
Smart-Agri-Tech
│
├── IoT
│   └── ESP32 Firmware
│
├── API
│   ├── app.py
│   ├── requirements.txt
│   └── templates
│
├── Dashboard
│
├── Models
│   ├── crop_recommender_model.pkl
│   └── expert_system_db.pkl
│
├── Notebooks
│
└── .gitignore
```

---

# 🚀 Installation

Clone repository

```bash
git clone https://github.com/NanawalaSaad/Smart-Agri-Tech.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run Flask

```bash
python app.py
```

---

# 🌍 Live Demo

https://smart-agri-tech.onrender.com

---

# 🔬 Future Improvements

- Machine Learning Based Prediction
- Disease Detection
- Weather Forecast Integration
- Mobile Application
- Historical Analytics
- Satellite Image Support
- Automatic Irrigation Control
- Multi-language Support

---

# 📚 Research Contribution

This project demonstrates the integration of:

- Internet of Things (IoT)
- Edge Computing
- Cloud Computing
- Expert System
- Precision Agriculture

The architecture can serve as a foundation for future research in smart agriculture for arid regions.

---

# 👨‍💻 Author

**Mohammad Saad Nanawala**

Computer Engineering

Government Engineering College Gandhinagar

India

---

## ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.
