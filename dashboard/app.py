import streamlit as st
import joblib
import numpy as np
import pickle
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="Desert AgriTech",
    page_icon="🌾",
    layout="wide"
)

# Load models
model = joblib.load(r'D:\desert-agritech\models\xgboost_yeild_model.pkl')

with open(r'D:\desert-agritech\models\crops_combined.pkl', 'rb') as f:
    crops_combined = pickle.load(f)

# CSS
st.markdown("""
<style>
    .main { background-color: #fef9f0; }
    .stButton button {
        background-color: #d97706;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
    }
    .metric-card {
        background: #fef3c7;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border-left: 4px solid #d97706;
    }
</style>
""", unsafe_allow_html=True)

# =====================
# SCORING FUNCTION
# =====================
WEIGHTS = {
    'temp': 0.25, 'humidity': 0.10, 'soil': 0.15,
    'ph': 0.20, 'light': 0.15, 'water': 0.10, 'nutrient': 0.05
}

def calculate_match_score(value, min_val, max_val):
    if min_val <= value <= max_val:
        center = (min_val + max_val) / 2
        range_half = (max_val - min_val) / 2
        if range_half == 0:
            return 100.0
        centrality = 1 - (abs(value - center) / range_half)
        return round(85 + (centrality * 15), 1)
    elif value < min_val:
        diff = min_val - value
        range_size = max_val - min_val
        if range_size == 0:
            return 0.0
        return round(max(0, 85 - (diff / range_size) * 85), 1)
    else:
        diff = value - max_val
        range_size = max_val - min_val
        if range_size == 0:
            return 0.0
        return round(max(0, 85 - (diff / range_size) * 85), 1)

def get_recommendations(temperature, humidity, soil_moisture,
                        pH_level, light_hours, water_given_ml,
                        nutrient_level, top_n=5):
    results = []
    for crop, info in crops_combined.items():
        ranges = info['ranges']
        extra = info['extra']
        temp_min, temp_max, hum_min, hum_max, soil_min, soil_max, \
        ph_min, ph_max, light_min, light_max, water_min, water_max, \
        nut_min, nut_max = ranges

        score = (
            calculate_match_score(temperature, temp_min, temp_max) * WEIGHTS['temp'] +
            calculate_match_score(humidity, hum_min, hum_max) * WEIGHTS['humidity'] +
            calculate_match_score(soil_moisture, soil_min, soil_max) * WEIGHTS['soil'] +
            calculate_match_score(pH_level, ph_min, ph_max) * WEIGHTS['ph'] +
            calculate_match_score(light_hours, light_min, light_max) * WEIGHTS['light'] +
            calculate_match_score(water_given_ml, water_min, water_max) * WEIGHTS['water'] +
            calculate_match_score(nutrient_level, nut_min, nut_max) * WEIGHTS['nutrient']
        )
        results.append({
            'crop': crop,
            'match_score': round(score, 1),
            'min_days': extra.get('min_days', 0),
            'max_days': extra.get('max_days', 0),
            'water_schedule': extra.get('water_schedule', 'N/A'),
            'harvest_tip': extra.get('harvest_tip', 'N/A')
        })

    results = sorted(results, key=lambda x: x['match_score'], reverse=True)
    top_score = results[0]['match_score']
    for r in results:
        r['match_score'] = round((r['match_score'] / top_score) * 100, 1)
    return results[:top_n]

# =====================
# SIDEBAR
# =====================
st.sidebar.image("https://img.icons8.com/emoji/96/seedling.png", width=60)
st.sidebar.title("🌾 Desert AgriTech")
st.sidebar.markdown("*World's First AI Desert Hydroponic System*")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "🏠 Home",
    "🎯 Yield Predictor",
    "🌱 Crop Recommendation",
    "📅 Growth Schedule",
    "📊 Model Insights"
])

st.sidebar.markdown("---")
st.sidebar.markdown("**Developed by:**")
st.sidebar.markdown("Mohammad Saad Nanawala")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/saad-nanawala-6160a72b0) | [GitHub](https://github.com/NanawalaSaad)")

# =====================
# HOME PAGE
# =====================
if page == "🏠 Home":
    st.title("🌾 Desert AgriTech")
    st.markdown("### *World's First AI-Powered Desert Hydroponic Intelligence System*")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Model Accuracy", "92.58%", "R² Score")
    with col2:
        st.metric("Desert Crops", "50", "Supported")
    with col3:
        st.metric("Training Data", "5,000", "Data Points")
    with col4:
        st.metric("IoT Sensors", "5+", "Integrated")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎯 What We Solve")
        st.info("Saudi Arabia imports 80%+ of its food. We built an AI system that tells farmers exactly what to grow, when to water, and how to optimize — even in 55°C desert heat.")
        st.markdown("### 🔧 Tech Stack")
        cols = st.columns(3)
        cols[0].success("XGBoost AI")
        cols[1].success("ESP32 IoT")
        cols[2].success("Flask API")
        cols = st.columns(3)
        cols[0].warning("Python")
        cols[1].warning("Streamlit")
        cols[2].warning("Vision 2030")

    with col2:
        st.markdown("### 🌍 Target Regions")
        st.markdown("""
        | Region | Use Case |
        |--------|----------|
        | 🇸🇦 Saudi Arabia | Primary — Vision 2030 food security |
        | 🇦🇪 UAE | Dubai vertical farms |
        | 🇮🇳 India (Rajasthan) | Thar desert hydroponic |
        """)
        st.markdown("### 📊 System Pipeline")
        st.markdown("""
            IoT Sensors → ESP32 → WiFi
            ↓
        Flask API → XGBoost Model
            ↓
        Yield + Crop + Schedule
                """)

# =====================
# YIELD PREDICTOR
# =====================
elif page == "🎯 Yield Predictor":
    st.title("🎯 Yield Predictor")
    st.markdown("Enter farm conditions to predict crop yield")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider("🌡️ Temperature (°C)", 35.0, 55.0, 42.0)
        humidity = st.slider("💧 Humidity (%)", 10.0, 40.0, 25.0)
        soil_moisture = st.slider("🌱 Soil Moisture (%)", 20.0, 80.0, 60.0)
        pH_level = st.slider("⚗️ pH Level", 5.5, 7.5, 6.5)
        light_hours = st.slider("☀️ Light Hours", 6.0, 14.0, 12.0)

    with col2:
        water_given_ml = st.slider("🚿 Water Given (ml)", 100.0, 500.0, 300.0)
        nutrient_level = st.slider("🧪 Nutrient Level (%)", 0.0, 100.0, 80.0)
        co2_ppm = st.slider("💨 CO2 (ppm)", 400.0, 1200.0, 800.0)
        day_number = st.slider("📆 Day Number", 1, 90, 45)

    if st.button("🔍 Predict Yield"):
        heat_stress_index = temperature * (1 - humidity/100)
        water_efficiency = water_given_ml / (soil_moisture + 1)
        pH_deviation = abs(pH_level - 6.5)
        growth_score = (light_hours * nutrient_level) / 100

        features = np.array([[
            temperature, humidity, soil_moisture, pH_level,
            light_hours, water_given_ml, nutrient_level, co2_ppm,
            day_number, heat_stress_index, water_efficiency,
            pH_deviation, growth_score
        ]])

        prediction = model.predict(features)[0]
        water_stress = soil_moisture < 30 or temperature > 45

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌾 Predicted Yield", f"{prediction:.2f} kg")
        with col2:
            status = "⚠️ High Risk" if water_stress else "✅ Healthy"
            st.metric("🌡 Plant Health", status)
        with col3:
            st.metric("📊 Growth Score", f"{growth_score:.2f}")

        if water_stress:
            st.error("⚠️ Water Stress Risk Detected! Increase irrigation or reduce temperature.")
        else:
            st.success("✅ Optimal conditions! Plant is healthy.")

# =====================
# CROP RECOMMENDATION
# =====================
elif page == "🌱 Crop Recommendation":
    st.title("🌱 Crop Recommendation")
    st.markdown("AI recommends best crops for your desert conditions")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider("🌡️ Temperature (°C)", 35.0, 55.0, 42.0, key="crop_temp")
        humidity = st.slider("💧 Humidity (%)", 10.0, 40.0, 25.0, key="crop_hum")
        soil_moisture = st.slider("🌱 Soil Moisture (%)", 20.0, 80.0, 60.0, key="crop_soil")
        pH_level = st.slider("⚗️ pH Level", 5.5, 7.5, 6.5, key="crop_ph")

    with col2:
        light_hours = st.slider("☀️ Light Hours", 6.0, 14.0, 12.0, key="crop_light")
        water_given_ml = st.slider("🚿 Water (ml)", 100.0, 500.0, 300.0, key="crop_water")
        nutrient_level = st.slider("🧪 Nutrients (%)", 0.0, 100.0, 80.0, key="crop_nut")
        top_n = st.selectbox("📋 Show Top", [5, 10, 15], index=0)

    if st.button("🌾 Get Recommendations"):
        recs = get_recommendations(
            temperature, humidity, soil_moisture,
            pH_level, light_hours, water_given_ml,
            nutrient_level, top_n=top_n
        )

        st.markdown("---")
        st.markdown(f"### 🏆 Top {top_n} Recommended Crops")

        for i, rec in enumerate(recs):
            with st.expander(f"{i+1}. {rec['crop']} — {rec['match_score']}% match"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Match Score", f"{rec['match_score']}%")
                col2.metric("Growth Days", f"{rec['min_days']}-{rec['max_days']}")
                col3.metric("Water Schedule", rec['water_schedule'])
                st.info(f"💡 Harvest Tip: {rec['harvest_tip']}")
                st.progress(rec['match_score'] / 100)

# =====================
# GROWTH SCHEDULE
# =====================
elif page == "📅 Growth Schedule":
    st.title("📅 Growth Schedule")
    st.markdown("Track your crop growth timeline")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider("🌡️ Temperature (°C)", 35.0, 55.0, 42.0, key="sched_temp")
        humidity = st.slider("💧 Humidity (%)", 10.0, 40.0, 25.0, key="sched_hum")
        soil_moisture = st.slider("🌱 Soil Moisture (%)", 20.0, 80.0, 60.0, key="sched_soil")
        pH_level = st.slider("⚗️ pH Level", 5.5, 7.5, 6.5, key="sched_ph")

    with col2:
        light_hours = st.slider("☀️ Light Hours", 6.0, 14.0, 12.0, key="sched_light")
        water_given_ml = st.slider("🚿 Water (ml)", 100.0, 500.0, 300.0, key="sched_water")
        nutrient_level = st.slider("🧪 Nutrients (%)", 0.0, 100.0, 80.0, key="sched_nut")
        days_grown = st.number_input("🌿 Days Already Grown", min_value=0, max_value=365, value=0)

    if st.button("📅 Get Schedule"):
        recs = get_recommendations(
            temperature, humidity, soil_moisture,
            pH_level, light_hours, water_given_ml,
            nutrient_level, top_n=3
        )

        st.markdown("---")
        st.markdown("### 🏆 Top 3 Crops With Growth Timeline")

        for i, rec in enumerate(recs):
            st.markdown(f"#### {i+1}. {rec['crop']} — {rec['match_score']}% match")

            progress = min(100, int((days_grown / rec['max_days']) * 100)) if rec['max_days'] > 0 else 0
            st.markdown(f"**Growth Progress: {progress}%**")
            st.progress(progress / 100)

            col1, col2, col3 = st.columns(3)
            col1.metric("Growth Days", f"{rec['min_days']}-{rec['max_days']}")
            col2.metric("Days Grown", days_grown)
            col3.metric("Days Remaining", max(0, rec['min_days'] - days_grown))

            if days_grown >= rec['min_days']:
                st.success("✅ Crop is ready to harvest!")
            else:
                st.warning(f"⏳ {rec['min_days'] - days_grown} more days until harvest")

            st.markdown("---")
# =====================
# MODEL INSIGHTS
# =====================
elif page == "📊 Model Insights":
    st.title("📊 Model Insights")
    st.markdown("XGBoost model performance and analysis")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("R² Accuracy", "92.58%")
    col2.metric("RMSE", "0.5413 kg")
    col3.metric("Training Samples", "5,000")

    st.markdown("---")
    st.markdown("### 📊 Feature Importance")

    features = ['growth_score', 'water_given_ml', 'temperature',
                'soil_moisture', 'light_hours', 'pH_deviation',
                'nutrient_level', 'humidity', 'co2_ppm',
                'heat_stress_index', 'water_efficiency', 'pH_level', 'day_number']
    importance = [0.6965, 0.1783, 0.0316, 0.0250, 0.0180,
                0.0120, 0.0100, 0.0090, 0.0080, 0.0060, 0.0040, 0.0010, 0.0006]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#d97706' if i == 0 else '#92400e' if i == 1 else '#fcd34d' for i in range(len(features))]
    ax.barh(features, importance, color=colors)
    ax.set_xlabel('Importance Score')
    ax.set_title('Feature Importance — What Matters Most for Yield')
    ax.invert_yaxis()
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")
    st.markdown("### 💡 Key Insights")
    st.info("**Growth Score** (light × nutrients) contributes 69.65% to yield prediction — light and nutrient management are the most critical factors in desert hydroponic farming.")
    st.warning("**Water Given** is the 2nd most important factor at 17.83% — precise irrigation scheduling is essential in water-scarce desert environments.")