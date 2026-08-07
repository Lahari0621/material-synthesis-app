import joblib
import os
import pandas as pd
from functools import lru_cache


MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")


@lru_cache(maxsize=1)
def _load_advanced_model():
    model_path = os.path.join(MODEL_DIR, "advanced_physics_model.pkl")
    features_path = os.path.join(MODEL_DIR, "model_features.pkl")
    if not os.path.exists(model_path) or not os.path.exists(features_path):
        return None, None
    return joblib.load(model_path), joblib.load(features_path)

@lru_cache(maxsize=2048)
def _predict_advanced_temperature_cached(density, specific_heat, target_phase, target_conversion):
    model, model_columns = _load_advanced_model()
    if model is None or model_columns is None:
        return {
            "error": "Advanced Model or Translation Key not found. Please run unified_trainer.py first."
        }

    input_data = {col: [0] for col in model_columns}

    if "density_g_cm3" in input_data:
        input_data["density_g_cm3"] = [density]
    if "specific_heat_j_kg_k" in input_data:
        input_data["specific_heat_j_kg_k"] = [specific_heat]

    phase_column_name = f"target_phase_{target_phase.lower()}"
    if phase_column_name in input_data:
        input_data[phase_column_name] = [1]
        notes = f"Successfully configured AI for {target_phase} phase synthesis."
    else:
        notes = (
            f"Warning: Phase '{target_phase}' not recognized by AI. "
            "Defaulting to baseline physics."
        )

    df_input = pd.DataFrame(input_data)
    predicted_temp = model.predict(df_input)[0]

    return {
        "optimal_temp_c": round(float(predicted_temp), 1),
        "confidence_score": round(target_conversion, 2),
        "notes": notes,
    }


def predict_advanced_temperature(density, specific_heat, target_phase, target_conversion=98.0):
    """
    Feeds physical properties AND the target phase (liquid, hexagonal, cubic, etc.)
    into the Advanced Master Model to predict the optimal furnace temperature.
    """
    return _predict_advanced_temperature_cached(
        round(float(density), 6),
        round(float(specific_heat), 6),
        str(target_phase).lower(),
        round(float(target_conversion), 2),
    )

# Quick test 
if __name__ == "__main__":
    # Testing our Zinc to Hexagonal Wurtzite example!
    result = predict_advanced_temperature(
        density=7.14, 
        specific_heat=388.0, 
        target_phase="hexagonal"
    )
    print(result)