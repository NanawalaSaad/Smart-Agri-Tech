from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
# Top pe add karo (imports ke baad)
import pickle






#FLASK APP BANAO
app = Flask(__name__)

#MODEL LOAD KARO
model = joblib.load(r'D:\desert-agritech\models\xgboost_yeild_model.pkl')
with open(r'D:\desert-agritech\models\crops_db.pkl', 'rb') as f:
    crops_db = pickle.load(f)
# crops_combined load karo (top pe, crops_db ke baad)
with open(r'D:\desert-agritech\models\crops_combined.pkl', 'rb') as f:
    crops_combined = pickle.load(f)

WEIGHTS = {
    'temp': 0.25, 'humidity': 0.10, 'soil': 0.15,
    'ph': 0.20, 'light': 0.15, 'water': 0.10, 'nutrient': 0.05
}

    
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    
    heat_stress_index = data['temperature'] * (1 - data['humidity']/100)
    water_efficiency = data['water_given_ml'] / (data['soil_moisture'] + 1)
    pH_deviation = abs(data['pH_level'] - 6.5)
    growth_score = (data['light_hours'] * data['nutrient_level']) / 100
    
    features = np.array([[
        data['temperature'], data['humidity'], data['soil_moisture'],
        data['pH_level'], data['light_hours'], data['water_given_ml'],
        data['nutrient_level'], data['co2_ppm'], data['day_number'],
        heat_stress_index, water_efficiency, pH_deviation, growth_score
    ]])
    
    prediction = model.predict(features)[0]
    
    water_stress = "High Risk" if (data['soil_moisture'] < 30 or data['temperature'] > 45) else "Healthy"
    
    return jsonify({
        "yield_kg": round(float(prediction), 2),
        "status": water_stress
    })
    
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

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    results = []

    for crop, ranges in crops_db.items():
        temp_min, temp_max, hum_min, hum_max, soil_min, soil_max, \
        ph_min, ph_max, light_min, light_max, water_min, water_max, \
        nut_min, nut_max = ranges

        weighted_score = (
            calculate_match_score(data['temperature'], temp_min, temp_max) * WEIGHTS['temp'] +
            calculate_match_score(data['humidity'], hum_min, hum_max) * WEIGHTS['humidity'] +
            calculate_match_score(data['soil_moisture'], soil_min, soil_max) * WEIGHTS['soil'] +
            calculate_match_score(data['pH_level'], ph_min, ph_max) * WEIGHTS['ph'] +
            calculate_match_score(data['light_hours'], light_min, light_max) * WEIGHTS['light'] +
            calculate_match_score(data['water_given_ml'], water_min, water_max) * WEIGHTS['water'] +
            calculate_match_score(data['nutrient_level'], nut_min, nut_max) * WEIGHTS['nutrient']
        )
        results.append({'crop': crop, 'match_score': round(weighted_score, 1)})

    results = sorted(results, key=lambda x: x['match_score'], reverse=True)
    top_score = results[0]['match_score']
    for r in results:
        r['match_score'] = round((r['match_score'] / top_score) * 100, 1)

    return jsonify({'recommendations': results[:10]})

# Schedule route
@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/schedule-recommend', methods=['POST'])
def schedule_recommend():
    data = request.json
    days_grown = data.get('days_grown', 0)
    results = []

    for crop, info in crops_combined.items():
        ranges = info['ranges']
        extra = info['extra']

        temp_min, temp_max, hum_min, hum_max, soil_min, soil_max, \
        ph_min, ph_max, light_min, light_max, water_min, water_max, \
        nut_min, nut_max = ranges

        weighted_score = (
            calculate_match_score(data['temperature'], temp_min, temp_max) * WEIGHTS['temp'] +
            calculate_match_score(data['humidity'], hum_min, hum_max) * WEIGHTS['humidity'] +
            calculate_match_score(data['soil_moisture'], soil_min, soil_max) * WEIGHTS['soil'] +
            calculate_match_score(data['pH_level'], ph_min, ph_max) * WEIGHTS['ph'] +
            calculate_match_score(data['light_hours'], light_min, light_max) * WEIGHTS['light'] +
            calculate_match_score(data['water_given_ml'], water_min, water_max) * WEIGHTS['water'] +
            calculate_match_score(data['nutrient_level'], nut_min, nut_max) * WEIGHTS['nutrient']
        )

        results.append({
            'crop': crop,
            'match_score': round(weighted_score, 1),
            'min_days': extra.get('min_days', 0),
            'max_days': extra.get('max_days', 0),
            'sowing_depth': extra.get('sowing_depth', 'N/A'),
            'water_schedule': extra.get('water_schedule', 'N/A'),
            'harvest_tip': extra.get('harvest_tip', 'N/A'),
            'days_grown': days_grown
        })

    results = sorted(results, key=lambda x: x['match_score'], reverse=True)
    top_score = results[0]['match_score']
    for r in results:
        r['match_score'] = round((r['match_score'] / top_score) * 100, 1)

    return jsonify({'recommendations': results[:5]})


#Prdict .......
@app.route('/predict-options')
def predict_options():
    return render_template('predict_options.html')

@app.route('/smart-predict', methods=['POST'])
def smart_predict():
    data = request.json
    mode = data.get('mode', 'yield')

    # Engineered features
    heat_stress_index = data['temperature'] * (1 - data['humidity']/100)
    water_efficiency = data['water_given_ml'] / (data['soil_moisture'] + 1)
    pH_deviation = abs(data['pH_level'] - 6.5)
    growth_score = (data['light_hours'] * data['nutrient_level']) / 100

    features = np.array([[
        data['temperature'], data['humidity'], data['soil_moisture'],
        data['pH_level'], data['light_hours'], data['water_given_ml'],
        data['nutrient_level'], data['co2_ppm'], data['day_number'],
        heat_stress_index, water_efficiency, pH_deviation, growth_score
    ]])

    yield_kg = round(float(model.predict(features)[0]), 2)
    water_stress = "High Risk" if (data['soil_moisture'] < 30 or data['temperature'] > 45) else "Healthy"

    if mode == 'yield':
        return jsonify({'yield_kg': yield_kg, 'status': water_stress})

    # Crop recommendation
    results = []
    for crop, info in crops_combined.items():
        ranges = info['ranges']
        extra = info['extra']

        temp_min, temp_max, hum_min, hum_max, soil_min, soil_max, \
        ph_min, ph_max, light_min, light_max, water_min, water_max, \
        nut_min, nut_max = ranges

        weighted_score = (
            calculate_match_score(data['temperature'], temp_min, temp_max) * WEIGHTS['temp'] +
            calculate_match_score(data['humidity'], hum_min, hum_max) * WEIGHTS['humidity'] +
            calculate_match_score(data['soil_moisture'], soil_min, soil_max) * WEIGHTS['soil'] +
            calculate_match_score(data['pH_level'], ph_min, ph_max) * WEIGHTS['ph'] +
            calculate_match_score(data['light_hours'], light_min, light_max) * WEIGHTS['light'] +
            calculate_match_score(data['water_given_ml'], water_min, water_max) * WEIGHTS['water'] +
            calculate_match_score(data['nutrient_level'], nut_min, nut_max) * WEIGHTS['nutrient']
        )

        results.append({
            'crop': crop,
            'match_score': round(weighted_score, 1),
            'yield_kg': yield_kg,
            'min_days': extra.get('min_days', 0),
            'max_days': extra.get('max_days', 0),
            'days_grown': data.get('days_grown', 0)
        })

    results = sorted(results, key=lambda x: x['match_score'], reverse=True)
    top_score = results[0]['match_score']
    for r in results:
        r['match_score'] = round((r['match_score'] / top_score) * 100, 1)

    return jsonify({'recommendations': results[:5]})

#m Insights
@app.route('/insights')
def insights():
    return render_template('insights.html')


#Hardware
@app.route('/hardware')
def hardware():
    return render_template('hardware.html')\
        
        
#contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

        

#about
@app.route('/about')
def about():
    return render_template('about.html')


#crop
@app.route('/crop')
def crop():
    return render_template('crop.html')


#protection
@app.route('/protection')
def protection():
    return render_template('protection.html')

#AI plybook
@app.route('/playbook')
def playbook():
    return render_template('playbook.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)