import pandas as pd
import joblib
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from data_prep import get_training_data

def train_ai():
    # 1. Get the data from our previous step
    df = get_training_data()
    if df is None: return

    # Create a folder to store our 'Brains'
    if not os.path.exists('models'):
        os.makedirs('models')

    # 2. Train a specific model for each material
    materials = df['material_name'].unique()
    
    for material in materials:
        print(f"🧠 AI is learning about: {material}...")
        
        # Filter data for this material
        mat_df = df[df['material_name'] == material]
        X = mat_df[['temp_celsius']] # Input
        y = mat_df['conversion_pct'] # Result

        # 3. Apply Polynomial Transformation (The 'Curve' math)
        # Degree 2 or 3 allows the AI to understand 'accelerating' reactions
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)

        # 4. Fit the Model
        model = LinearRegression()
        model.fit(X_poly, y)

        # 5. Save the Brain (Model) and the Math (Poly)
        joblib.dump(model, f'models/{material}_model.pkl')
        joblib.dump(poly, f'models/{material}_poly.pkl')
        
        print(f"✅ Training complete for {material}. Model saved in /models/")

if __name__ == "__main__":
    train_ai()