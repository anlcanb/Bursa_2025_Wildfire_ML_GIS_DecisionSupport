import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

def main():
    # 1. Veri Setinin Yüklenmesi
    data_path = 'data/dataset.csv'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"{data_path} bulunamadı! Lütfen dataset.csv dosyasının 'data/' klasöründe olduğundan emin olun.")
    
    df = pd.read_csv(data_path)
    print("=== 1. Veri Yapısı İnceleme ===")
    print(f"Toplam Satır: {df.shape[0]}, Toplam Sütun: {df.shape[1]}")
    
    # Model girdisi olacak 15 öznitelik ve hedef değişken
    features = [
        'preNDVI', 'postNDVI', 'dNDVI', 
        'preNBR', 'postNBR', 'dNBR', 
        'preNDMI', 'postNDMI', 'dNDMI', 
        'elevation', 'slope', 'aspect', 
        'landcover', 'preNIR', 'postNIR'
    ]
    target = 'label'
    
    # Olası sütun adı uyuşmazlıklarına karşı kontrol
    available_features = [col for col in features if col in df.columns]
    if len(available_features) < len(features):
        print(f"[UYARI] Eksik sütunlar var. Mevcut olanlar kullanılacak: {available_features}")
        features = available_features

    # 2. Temizlik (Eksik veya sonsuz değerlerin elenmesi)
    # GEE bazen sınır piksellerde NaN veya Inf üretebilir, bunları temizliyoruz
    df_clean = df.replace([np.inf, -np.inf], np.nan).dropna(subset=features + [target])
    print(f"Temizlik sonrası güvenli satır sayısı: {df_clean.shape[0]}")
    
    X = df_clean[features]
    y = df_clean[target].astype(int)
    
    # 3. Eğitim ve Test Seti Ayrımı (%80 Eğitim, %20 Test)
    # Stratify kullanarak yanan ve yanmayan noktaların dengeli dağılmasını sağlıyoruz
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Eğitim Seti Boyutu: {X_train.shape[0]}, Test Seti Boyutu: {X_test.shape[0]}")
    
    # 4. Veri Ölçekleme (Standardization)
    # SVM ve XGBoost adımlarında da tutarlılık sağlamak için veriyi normalize ediyoruz
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Modeller klasörünü oluşturup ölçekleyiciyi kaydedelim
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, 'models/scaler.pkl')
    
    # 5. Baseline Random Forest Modelinin Kurulması
    print("\n=== 2. Random Forest Modeli Eğitiliyor ===")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train_scaled, y_train)
    
    # 6. Model Tahmini ve Metrikler
    y_pred = rf_model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n=== 3. Model Performans Sonuçları ===")
    print(f"Doğruluk (Accuracy) Skoru: %{acc * 100:.2f}")
    print("\nAyrıntılı Sınıflandırma Raporu:")
    print(classification_report(y_test, y_pred))
    
    print("Konfüzyon Matrisi (Confusion Matrix):")
    print(confusion_matrix(y_test, y_pred))
    
    # Modeli kaydetme
    joblib.dump(rf_model, 'models/random_forest_model.pkl')
    print("\n[BAŞARILI] Random Forest modeli 'models/random_forest_model.pkl' olarak kaydedildi.")
    
    # 7. Öznitelik Önem Dereceleri (Feature Importance)
    importances = rf_model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    print("\n=== 4. Öznitelik Önem Sıralaması (Feature Importance) ===")
    for f in range(X_train.shape[1]):
        print(f"{f + 1}. {X_train.columns[indices[f]]}: %{importances[indices[f]] * 100:.2f}")

if __name__ == '__main__':
    main()