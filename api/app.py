from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pickle
import os

app = Flask(__name__)
CORS(app)

# --- GLOBAL LIVE SENSOR MEMORY (ALL HARDWARE SENSORS) ---
live_sensor_data = {
    'temperature': 0.0, 
    'humidity': 0.0, 
    'soil_moisture': 0.0, 
    'pH_level': 0.0, 
    'light_hours': 0.0, 
    'rain_status': 0.0,         # Rain Sensor
    'ultrasonic_distance': 0.0, # Ultrasonic Distance Sensor
    'water_given_ml': 0.0, 
    'nutrient_level': 0.0
}

# --- LOAD EXPERT SYSTEM DATABASE ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../models/expert_system_db.pkl')
try:
    with open(MODEL_PATH, 'rb') as f:
        crops_db = pickle.load(f)
    print(f"✅ Loaded {len(crops_db)} crops successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    crops_db = []

# --- CORE ENGINE: CATEGORY & SCALING LOGIC (WITH SCHEDULE) ---
def get_categorized_matches(sensor_data, top_n=3):
    temp_results = {'Tree': [], 'Plant': [], 'Dry Fruit': []}
    final_results = {'Tree': [], 'Plant': [], 'Dry Fruit': []}
    
    for crop in crops_db:
        score, total = 0, 0
        
        t = sensor_data.get('temperature', 30)
        if crop['temp_min'] <= t <= crop['temp_max']: score += 25
        elif abs(t - crop['temp_min']) <= 5 or abs(t - crop['temp_max']) <= 5: score += 12
        total += 25
        
        h = sensor_data.get('humidity', 50)
        if crop['humidity_min'] <= h <= crop['humidity_max']: score += 20
        elif abs(h - crop['humidity_min']) <= 10 or abs(h - crop['humidity_max']) <= 10: score += 10
        total += 20
        
        s = sensor_data.get('soil_moisture', 40)
        if crop['soil_moisture_min'] <= s <= crop['soil_moisture_max']: score += 20
        elif abs(s - crop['soil_moisture_min']) <= 10 or abs(s - crop['soil_moisture_max']) <= 10: score += 10
        total += 20
        
        p = sensor_data.get('pH_level', 6.5)
        if crop['ph_min'] <= p <= crop['ph_max']: score += 15
        elif abs(p - crop['ph_min']) <= 0.5 or abs(p - crop['ph_max']) <= 0.5: score += 7
        total += 15

        score += crop.get('priority', 5) * 0.5
        raw_pct = (score / (total + 5)) * 100
        
        cat = crop.get('category', 'Plant')
        if cat in temp_results:
            temp_results[cat].append({
                'raw_pct': raw_pct,
                'crop': crop['name'],
                'grow_days': crop['grow_days'],
                'water_need': crop['water_need']
            })

    for cat, crops in temp_results.items():
        if not crops: continue
        max_raw = max(c['raw_pct'] for c in crops)
        for c in crops:
            c['match_score'] = round((c['raw_pct'] / max_raw) * 99.0, 1) if max_raw > 0 else 0
            c['min_days'] = max(10, c['grow_days'] - 10)
            c['max_days'] = c['grow_days'] + 10
            c['yield_kg'] = round((c['match_score'] / 100) * 8.5, 2)
            c['sowing_depth'] = "3-5 cm"
            
            if c['water_need'] == 'High':
                c['water_schedule'] = "Water twice daily: 7:00 AM & 5:00 PM (Keep soil 90%+ moist)"
                c['fertilizer'] = "Add Nitrogen-based fertilizer every 20 days"
            else:
                c['water_schedule'] = "Water once: 8:00 AM (Only when topsoil is dry)"
                c['fertilizer'] = "Add Organic Compost once a month"
                
            c['sunlight'] = "6-8 hours of direct sunlight required"
            
        crops.sort(key=lambda x: x['match_score'], reverse=True)
        final_results[cat] = crops[:top_n]

    return final_results

# --- HTML ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/sensors')
def sensors(): return render_template('sensors.html')

@app.route('/predict-options')
def predict_options(): return render_template('predict_options.html')

@app.route('/crop')
def crop(): return render_template('crop.html')

@app.route('/schedule')
def schedule(): return render_template('schedule.html')

@app.route('/hardware')
def hardware(): return render_template('hardware.html')

@app.route('/protection')
def protection(): return render_template('protection.html')

@app.route('/playbook')
def playbook(): return render_template('playbook.html')

@app.route('/insights')
def insights(): return render_template('insights.html')

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/contact')
def contact(): return render_template('contact.html')

# --- IOT LIVE DATA ENDPOINTS ---
@app.route('/api/sensor-update', methods=['POST'])
def sensor_update():
    global live_sensor_data
    data = request.json
    live_sensor_data.update(data)
    return jsonify({"status": "success"})

@app.route('/api/live-sensor', methods=['GET'])
def get_live_sensor():
    return jsonify(live_sensor_data)

# --- PREDICTION API WITH FAILSAFE ---
@app.route('/smart-predict', methods=['POST'])
def smart_predict():
    data = request.json
    mode = data.get('mode', 'yield')
    days_grown = data.get('days_grown', 0)
    
    if live_sensor_data['temperature'] == 0 and live_sensor_data['soil_moisture'] == 0:
        return jsonify({'status': 'HARDWARE ERROR: Sensors disconnected!', 'yield_kg': 0, 'error': True})
    
    moist = live_sensor_data['soil_moisture']
    status = 'Healthy' if moist > 30 else 'Water Stress Risk'
    yld = round((moist / 100) * 8.5, 2)
    response = {'status': status, 'yield_kg': yld, 'error': False}
    
    if mode != 'yield':
        matches = get_categorized_matches(live_sensor_data, top_n=3)
        for cat in matches:
            for m in matches[cat]: m['days_grown'] = days_grown
        response['recommendations'] = matches
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)