import joblib
import numpy as np
import os

def get_optimal_temperature(material_name, target_conversion=95.0):
    """
    Loads the trained model for a material and finds the lowest temperature 
    required to hit the target conversion percentage.
    """
    model_path = f'models/{material_name}_model.pkl'
    poly_path = f'models/{material_name}_poly.pkl'

    # Check if the AI has learned about this material yet
    if not os.path.exists(model_path) or not os.path.exists(poly_path):
        return {"error": f"No trained AI model found for {material_name}."}

    # Load the Brain and the Math
    model = joblib.load(model_path)
    poly = joblib.load(poly_path)

    # Generate a simulation range of temperatures (e.g., from 0°C to 2500°C)
    # We test every single degree to find the exact optimal point
    temps_to_test = np.arange(0, 2500, 1).reshape(-1, 1) 
    
    # Apply the polynomial transformation to our test temperatures
    temps_poly = poly.transform(temps_to_test)
    
    # Predict the conversion percentage for all 2500 temperatures instantly
    predictions = model.predict(temps_poly)
    
    # Find the first temperature where the predicted conversion hits our target
    for temp, pred in zip(temps_to_test, predictions):
        if pred >= target_conversion:
            return {
                "material": material_name,
                "optimal_temp_c": round(float(temp[0]), 1),
                "achieved_conversion_pct": round(float(pred), 2)
            }
            
    return {"error": "Target conversion not reachable within 2500°C limit."}

# Quick test to see if it works
if __name__ == "__main__":
    # Assuming you have trained a model for 'Iron Ore'
    result = get_optimal_temperature('Iron Ore', target_conversion=98.0)
    print(result)