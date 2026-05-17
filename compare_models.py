import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import joblib

# Gradient Boosting / XGBoost kontrolü
try:
    from xgboost import XGBClassifier
    XGB_AVAILABLE = True
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier
    XGB_AVAILABLE = False

def main():
    # 1. Veri Hazırlığı
    df = pd.read_csv('data/dataset.csv')
    features = [
        'preNDVI', 'postNDVI', 'dNDVI', 
        'preNBR', 'postNBR', 'dNBR', 
        'preNDMI', 'postNDMI', 'dNDMI', 
        'elevation', 'slope', 'aspect', 
        'landcover', 'preNIR', 'postNIR'
    ]
    target = 'label'
    
    df_clean = df.replace([np.inf, -np.inf], np.nan).dropna(subset=features + [target])
    X = df_clean[features]
    y = df_clean[target].astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 2. Modellerin Tanımlanması
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        'Support Vector Machine': SVC(probability=True, random_state=42)
    }
    
    if XGB_AVAILABLE:
        print("[BİLGİ] XGBoost kütüphanesi bulundu, XGBoost eğitilecek.")
        models['XGBoost'] = XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss', n_jobs=-1)
    else:
        print("[BİLGİ] XGBoost bulunamadı, varsayılan Scikit-Learn Gradient Boosting eğitilecek.")
        models['Gradient Boosting'] = GradientBoostingClassifier(n_estimators=100, random_state=42)
        
    # 3. Modellerin Eğitilmesi ve Metriklerin Toplanması
    results = []
    os.makedirs('models', exist_ok=True)
    
    print("\n=== Modeller Eğitiliyor ve Karşılaştırılıyor ===")
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        
        # Test performansı
        y_pred = model.predict(X_test_scaled)
        
        # Metriklerin el ile hesaplanması (Karşılaştırma tablosu için)
        tp = np.sum((y_test == 1) & (y_pred == 1))
        tn = np.sum((y_test == 0) & (y_pred == 0))
        fp = np.sum((y_test == 0) & (y_pred == 1))
        fn = np.sum((y_test == 1) & (y_pred == 0))
        
        accuracy = (tp + tn) / len(y_test)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        results.append({
            'Model': name,
            'Accuracy': f"{accuracy*100:.2f}%",
            'Precision': f"{precision*100:.2f}%",
            'Recall': f"{recall*100:.2f}%",
            'F1-Score': f"{f1_score*100:.2f}%"
        })
        
        # Her modeli gelecekte harita üretimi için kaydedelim
        model_filename = f"models/{name.lower().replace(' ', '_')}_model.pkl"
        joblib.dump(model, model_filename)
        print(f"-> {name} eğitildi ve '{model_filename}' olarak kaydedildi.")
        
    # 4. Karşılaştırma Tablosunu Ekrana Yazdırma
    results_df = pd.DataFrame(results)
    print("\n=======================================================")
    print("          AKADEMİK MODEL KARŞILAŞTIRMA TABLOSU         ")
    print("=======================================================")
    print(results_df.to_string(index=False))
    print("=======================================================")
    
if __name__ == '__main__':
    main()