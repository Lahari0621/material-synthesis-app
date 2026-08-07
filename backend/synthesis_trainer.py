import pandas as pd
import joblib
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error

def train_synthesis_model():
    """
    Train a comprehensive material synthesis model that:
    1. Predicts FEASIBILITY of transformations (Classification)
    2. Predicts the ACTUAL TARGET COMPOUND (Classification)
    3. Predicts the REQUIRED TEMPERATURE (Regression)
    """
    print("🚀 Training Advanced Material Synthesis Model...")
    
    try:
        df = pd.read_csv('material_synthesis_dataset.csv')
        print(f"✔ Dataset loaded! Found {len(df)} records.")
        print(df.head())
    except FileNotFoundError:
        print("❌ Error: 'material_synthesis_dataset.csv' not found.")
        return

    # ============================================
    # 1. FEASIBILITY MODEL (Classification)
    # ============================================
    print("\n📊 Training Feasibility Classifier...")
    
    # Features for feasibility
    X_feasibility = df[['density_g_cm3', 'specific_heat_j_kg_k']]
    y_feasibility = df['is_feasible'].astype(int)
    
    # Add material pair encoding
    df['material_pair'] = df['base_material'] + '_to_' + df['target_material']
    le_pair = LabelEncoder()
    df['material_pair_encoded'] = le_pair.fit_transform(df['material_pair'])
    
    X_feasibility['material_pair'] = df['material_pair_encoded']
    
    X_train_f, X_test_f, y_train_f, y_test_f = train_test_split(
        X_feasibility, y_feasibility, test_size=0.2, random_state=42
    )
    
    feasibility_model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10)
    feasibility_model.fit(X_train_f, y_train_f)
    
    feasibility_acc = accuracy_score(y_test_f, feasibility_model.predict(X_test_f))
    print(f"✔ Feasibility Model Accuracy: {round(feasibility_acc * 100, 2)}%")
    
    # ============================================
    # 2. TARGET COMPOUND MODEL (Classification)
    # ============================================
    print("\n🎯 Training Target Compound Classifier...")
    
    # Only train on feasible transformations
    df_feasible = df[df['is_feasible'] == 1].copy()
    
    X_compound = df_feasible[['density_g_cm3', 'specific_heat_j_kg_k']].copy()
    X_compound['material_pair'] = df_feasible['material_pair_encoded'].values
    
    y_compound = df_feasible['target_compound']
    le_compound = LabelEncoder()
    y_compound_encoded = le_compound.fit_transform(y_compound)
    
    if len(X_compound) > 5:  # Ensure enough samples
        X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
            X_compound, y_compound_encoded, test_size=0.2, random_state=42
        )
        
        compound_model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10)
        compound_model.fit(X_train_c, y_train_c)
        
        compound_acc = accuracy_score(y_test_c, compound_model.predict(X_test_c))
        print(f"✔ Target Compound Model Accuracy: {round(compound_acc * 100, 2)}%")
    else:
        compound_model = None
        print("⚠ Insufficient data for Compound Model")
    
    # ============================================
    # 3. TEMPERATURE MODEL (Regression)
    # ============================================
    print("\n🌡️ Training Temperature Prediction Model...")
    
    # Only use feasible transformations
    X_temp = df_feasible[['density_g_cm3', 'specific_heat_j_kg_k']].copy()
    X_temp['material_pair'] = df_feasible['material_pair_encoded'].values
    
    y_temp = df_feasible['required_temp_c']
    
    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
        X_temp, y_temp, test_size=0.2, random_state=42
    )
    
    temp_model = RandomForestRegressor(n_estimators=100, random_state=42)
    temp_model.fit(X_train_t, y_train_t)
    
    temp_mae = mean_absolute_error(y_test_t, temp_model.predict(X_test_t))
    print(f"✔ Temperature Model MAE: ±{round(temp_mae, 2)}°C")
    
    # ============================================
    # 4. SAVE ALL MODELS
    # ============================================
    print("\n💾 Saving models...")
    
    if not os.path.exists('models'):
        os.makedirs('models')
    
    joblib.dump(feasibility_model, 'models/feasibility_model.pkl')
    joblib.dump(le_pair, 'models/material_pair_encoder.pkl')
    
    if compound_model:
        joblib.dump(compound_model, 'models/compound_model.pkl')
        joblib.dump(le_compound, 'models/compound_encoder.pkl')
    
    joblib.dump(temp_model, 'models/temperature_model.pkl')
    
    # Create a mapping dictionary for quick lookups
    transformation_map = {}
    for idx, row in df.iterrows():
        key = f"{row['base_material'].lower()}_{row['target_material'].lower()}"
        transformation_map[key] = {
            'target_compound': row['target_compound'],
            'is_feasible': bool(row['is_feasible']),
            'required_temp': row['required_temp_c'],
            'confidence': row['confidence_pct'],
            'notes': row['notes']
        }
    
    joblib.dump(transformation_map, 'models/transformation_map.pkl')
    
    print("✅ All models trained and saved successfully!")
    print(f"📚 Transformation database: {len(transformation_map)} entries")

if __name__ == "__main__":
    train_synthesis_model()
