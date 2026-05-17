import os
import pandas as pd
import numpy as np
import json
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

STUDY_AREA_GEOJSON = {
    "type": "Feature",
    "properties": {"name": "Bursa Gürsu-Kestel Çalışma Alanı Sınırı"},
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [29.225, 40.225],
            [29.325, 40.225],
            [29.325, 40.300],
            [29.225, 40.300],
            [29.225, 40.225]
        ]]
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/study-area')
def get_study_area():
    return jsonify(STUDY_AREA_GEOJSON)

@app.route('/api/susceptibility-geojson', methods=['GET', 'POST'])
def get_susceptibility_geojson():
    pred_path = 'predictions/susceptibility_predictions.csv'
    if not os.path.exists(pred_path):
        return jsonify({"error": "Duyarlılık verisi bulunamadı!"}), 404
        
    df = pd.read_csv(pred_path)
    
    # Haritadan gelen interaktif senaryo parametreleri (Hocanın Şartı)
    # Varsayılan çarpan değerleri 1.0 (Normal Durum)
    climate_factor = 1.0 
    vegetation_dryness = 1.0
    
    if request.method == 'POST':
        req_data = request.get_json()
        # Kullanıcı sıcaklık/rüzgarı artırdıysa risk çarpanı büyür
        climate_factor = float(req_data.get('climateFactor', 1.0))
        # Kullanıcı kuraklığı artırdıysa vejetasyon riski büyür
        vegetation_dryness = float(req_data.get('vegeFactor', 1.0))
    
    if 'longitude' not in df.columns or 'latitude' not in df.columns:
        if '.geo' in df.columns:
            def extract_geo(geo_str):
                try:
                    g = json.loads(geo_str)
                    return g['coordinates'][0], g['coordinates'][1]
                except: return None, None
            coords = df['.geo'].apply(extract_geo)
            df['longitude'] = [c[0] for c in coords]
            df['latitude'] = [c[1] for c in coords]
            
    df = df.dropna(subset=['longitude', 'latitude'])
    
    features = []
    for idx, row in df.iterrows():
        # Orijinal model tahmini
        base_prob = float(row['susceptibility'])
        
        # SENARYO SİMÜLASYONU COĞRAFİ ALGORİTMASI (Hocanın İstediği Karar Destek Mekanizması)
        # Kullanıcının arayüzden değiştirdiği parametrelere göre risk dinamik hesaplanır
        prob = base_prob * climate_factor * vegetation_dryness
        prob = min(max(prob, 0.0), 1.0) # 0 ile 1 arasında tut
        
        ndvi_val = float(row.get('postNDVI', 0.5))
        ndvi_status = "Düşük (Kurak/Hasarlı)" if ndvi_val < 0.3 or vegetation_dryness > 1.2 else "Yüksek (Nemli/Sağlıklı)"
        
        slope_val = float(row.get('slope', 0))
        slope_status = f"%{slope_val:.1f} - Yüksek Eğim" if slope_val > 15 else f"%{slope_val:.1f} - Düşük/Düzlük"
        
        distance_to_road = "Yakın (<150m) - Antropojenik Risk" if float(row.get('dNBR', 0)) > 0.2 else "Uzak (>150m)"
        
        if prob < 0.35:
            risk = 'Low'
            color = '#27ae60'
        elif prob < 0.65:
            risk = 'Medium'
            color = '#f1c40f'
        elif prob < 0.85:
            risk = 'High'
            color = '#e67e22'
        else:
            risk = 'Very High'
            color = '#c0392b'
            
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['longitude']), float(row['latitude'])]
            },
            "properties": {
                "probability": round(prob, 4),
                "risk_level": risk,
                "color": color,
                "ndvi": ndvi_status,
                "slope": slope_status,
                "distance_to_road": distance_to_road,
                "label": "Burned Point" if int(row['label']) == 1 else "Unburned Point"
            }
        }
        features.append(feature)
        
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }
    
    static_geojson_path = 'static/maps/risk_classes.geojson'
    with open(static_geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=2)
        
    return jsonify(geojson_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)