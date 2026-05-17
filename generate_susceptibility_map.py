import os
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def extract_coordinates(df):
    """
    Extract longitude and latitude from GEE .geo column if needed.
    """
    if "longitude" in df.columns and "latitude" in df.columns:
        return df

    if ".geo" in df.columns:
        def parse_geo(geo_str):
            try:
                g = json.loads(geo_str)
                return g["coordinates"][0], g["coordinates"][1]
            except Exception:
                return None, None

        coords = df[".geo"].apply(parse_geo)
        df["longitude"] = [c[0] for c in coords]
        df["latitude"] = [c[1] for c in coords]

    return df


def classify_risk(prob):
    """
    Convert probability value into wildfire susceptibility class.
    """
    if prob < 0.25:
        return "Low"
    elif prob < 0.50:
        return "Medium"
    elif prob < 0.75:
        return "High"
    else:
        return "Very High"


def main():
    data_path = "data/dataset.csv"

    if not os.path.exists(data_path):
        raise FileNotFoundError("data/dataset.csv bulunamadı.")

    df = pd.read_csv(data_path)

    # Important:
    # For susceptibility mapping, avoid post-fire burn-severity leakage.
    # dNBR, dNDVI, dNDMI, postNBR, postNDVI etc. directly describe fire impact.
    # Instead, use pre-fire and terrain-related variables.
    susceptibility_features = [
        "preNDVI",
        "preNBR",
        "preNDMI",
        "elevation",
        "slope",
        "aspect",
        "landcover",
        "preNIR"
    ]

    target = "label"

    missing = [col for col in susceptibility_features + [target] if col not in df.columns]
    if missing:
        raise ValueError(f"Eksik sütunlar var: {missing}")

    df = extract_coordinates(df)

    df_clean = df.replace([np.inf, -np.inf], np.nan).copy()
    df_clean[susceptibility_features] = df_clean[susceptibility_features].fillna(
        df_clean[susceptibility_features].median()
    )

    df_clean = df_clean.dropna(subset=[target, "longitude", "latitude"])

    X = df_clean[susceptibility_features]
    y = df_clean[target].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Regularized Random Forest:
    # max_depth and min_samples_leaf prevent extremely hard 0/1 probabilities.
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=6,
        min_samples_leaf=8,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)

    print("\n=== Susceptibility Model Performance ===")
    print(f"Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Predict probabilities for all available points
    X_all_scaled = scaler.transform(df_clean[susceptibility_features])
    probabilities = model.predict_proba(X_all_scaled)[:, 1]

    df_clean["susceptibility"] = probabilities
    df_clean["risk_class"] = df_clean["susceptibility"].apply(classify_risk)

    print("\n=== Risk Class Distribution ===")
    print(df_clean["risk_class"].value_counts())

    os.makedirs("models", exist_ok=True)
    os.makedirs("predictions", exist_ok=True)

    joblib.dump(model, "models/susceptibility_random_forest_model.pkl")
    joblib.dump(scaler, "models/susceptibility_scaler.pkl")

    with open("models/susceptibility_features.json", "w", encoding="utf-8") as f:
        json.dump(susceptibility_features, f, indent=2)

    output_path = "predictions/susceptibility_predictions.csv"
    df_clean.to_csv(output_path, index=False)

    print(f"\n[BAŞARILI] Susceptibility predictions saved to: {output_path}")


if __name__ == "__main__":
    main()