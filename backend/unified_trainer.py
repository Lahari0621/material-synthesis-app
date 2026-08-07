import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

def train_advanced_model():
    print("🚀 Initializing Advanced Physics & Phase Model Training...")
    
    try:
        df = pd.read_csv('advanced_material_properties.csv')
        print(f"✔ Dataset loaded! Found {len(df)} records.")
    except FileNotFoundError:
        print("❌ Error: 'advanced_material_properties.csv' not found.")
        return

    # 1. The "Translator": One-Hot Encoding
    print("🧮 Translating chemistry words into math (One-Hot Encoding)...")
    
    # We drop base_material because the AI shouldn't memorize names, only physics!
    X = df.drop(columns=['base_material', 'required_temp_c'])
    y = df['required_temp_c']

    # This magically turns 'target_phase' into binary math columns
    X_encoded = pd.get_dummies(X, columns=['target_phase'])

    # 2. Split Data for Testing
    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

    # 3. Train the Brain
    print("🧠 AI is learning advanced solid-state physics...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 4. Test Accuracy
    predictions = model.predict(X_test)
    error = mean_absolute_error(y_test, predictions)
    print(f"🎯 Accuracy check: Predictions are off by an average of ±{round(error, 2)}°C")

    # 5. Save the Brain AND the Translation Key
    if not os.path.exists('models'):
        os.makedirs('models')
        
    joblib.dump(model, 'models/advanced_physics_model.pkl')
    
    # We MUST save the column names so Flask knows how to talk to the AI later
    joblib.dump(list(X_encoded.columns), 'models/model_features.pkl') 
    
    print("✅ Training complete! Brain and Translation Key saved in 'models/'.")

if __name__ == "__main__":
    train_advanced_model()