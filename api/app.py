from flask import Flask,request,jsonify
import joblib
import numpy as np
import json
import pickle
with open(r'D:\desert-agritech\models\crops_db.pkl', 'rb') as f:
    crops_db = pickle.load(f)
#flask app banao
app=Flask(__name__)

#model load karo
model=joblib.load(r'D:\desert-agritech\models\xgboost_yeild_model.pkl')
print("Model Loaded")

#home route
@app.route('/')
def home():
    return jsonify({
        "message":"Desert Agritech API",
        "status":"running"
    })
    
    
#predict Route
@app.route('/predict',methods=['POST'])
def predict():
    data=request.json
    
    #input values lo
    features=np.array([[
        data['temperature'],
        data['humidity'],
        data['soil_moisture'],
        data['pH_level'],
        data['light_hours'],
        data['water_given_ml'],
        data['nutrient_level'],
        data['co2_ppm'],
        data['day_number'],
        data['heat_stress_index'],
        data['water_efficiency'],
        data['pH_deviation'],
        data['growth_score']
    ]])
    
    #prediction karo
    prediction=model.predict(features)[0]
    
    return jsonify({
        "yield_kg":round(float(prediction),2),
        "status":"success"
    })
    

# Function ko test karke output save karo
def calculate_match_score(value, min_val, max_val):
    if min_val <= value <= max_val:
        return 100.0
    elif value < min_val:
        diff = min_val - value
        range_size = max_val - min_val
        return max(0, 100 - (diff / range_size) * 100)
    else:
        diff = value - max_val
        range_size = max_val - min_val
        return max(0, 100 - (diff / range_size) * 100)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    results = []
    
    for crop, ranges in crops_db.items():
        temp_min, temp_max, hum_min, hum_max, soil_min, soil_max, \
        ph_min, ph_max, light_min, light_max, water_min, water_max, \
        nut_min, nut_max = ranges
        
        score = (
            calculate_match_score(data['temperature'], temp_min, temp_max) +
            calculate_match_score(data['humidity'], hum_min, hum_max) +
            calculate_match_score(data['soil_moisture'], soil_min, soil_max) +
            calculate_match_score(data['pH_level'], ph_min, ph_max) +
            calculate_match_score(data['light_hours'], light_min, light_max) +
            calculate_match_score(data['water_given_ml'], water_min, water_max) +
            calculate_match_score(data['nutrient_level'], nut_min, nut_max)
        ) / 7
        
        results.append({
            'crop': crop,
            'match_score': round(score, 1)
        })
    
    results = sorted(results, key=lambda x: x['match_score'], reverse=True)
    
    return jsonify({'recommendations': results[:5]})

    
#run
if __name__=='__main__':
    app.run(debug=True,port=5000)
