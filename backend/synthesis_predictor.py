import joblib
import os
import pandas as pd
from mendeleev import element
from functools import lru_cache


MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")


@lru_cache(maxsize=1)
def _load_models():
    """Load immutable prediction resources once per server process."""
    required_files = {
        "feasibility_model": "feasibility_model.pkl",
        "pair_encoder": "material_pair_encoder.pkl",
        "temperature_model": "temperature_model.pkl",
        "transformation_map": "transformation_map.pkl",
    }
    missing = [
        filename
        for filename in required_files.values()
        if not os.path.exists(os.path.join(MODEL_DIR, filename))
    ]
    if missing:
        raise FileNotFoundError(
            f"Model file '{missing[0]}' not found. Please run synthesis_trainer.py first."
        )

    resources = {
        name: joblib.load(os.path.join(MODEL_DIR, filename))
        for name, filename in required_files.items()
    }

    compound_path = os.path.join(MODEL_DIR, "compound_model.pkl")
    compound_encoder_path = os.path.join(MODEL_DIR, "compound_encoder.pkl")
    resources["compound_model"] = (
        joblib.load(compound_path) if os.path.exists(compound_path) else None
    )
    resources["compound_encoder"] = (
        joblib.load(compound_encoder_path)
        if os.path.exists(compound_encoder_path)
        else None
    )
    return resources


def get_transformation_map():
    return _load_models()["transformation_map"]


@lru_cache(maxsize=1)
def _transformation_index():
    """O(1) lookup index: (base, target) -> transformation info."""
    index = {}
    for key, info in get_transformation_map().items():
        parts = key.split("_to_")
        if len(parts) == 2:
            index[(parts[0], parts[1])] = info
        else:
            index[(key, "")] = info
    return index


@lru_cache(maxsize=512)
def normalize_material_name(material):
    """Return a canonical material token for lookup.

    Element names and symbols are normalized to the chemical symbol so that
    inputs like "zinc", "Zinc", and "Zn" all resolve to "Zn".
    Non-element names are preserved with trimmed whitespace.
    """
    if material is None:
        return None

    cleaned = str(material).strip()
    if not cleaned:
        return cleaned

    candidates = []
    title_case = cleaned.title()
    capitalized = cleaned.capitalize()
    for candidate in (cleaned, capitalized, title_case):
        if candidate not in candidates:
            candidates.append(candidate)

    try:
        for candidate in candidates:
            try:
                return element(candidate).symbol
            except Exception:
                continue
    except Exception:
        return cleaned

    return cleaned

@lru_cache(maxsize=2048)
def _predict_material_synthesis_cached(base_material, target_material, density, specific_heat):
    return _predict_material_synthesis_uncached(
        base_material, target_material, density, specific_heat
    )


def predict_material_synthesis(base_material, target_material, density=None, specific_heat=None):
    """
    Comprehensive material synthesis prediction.
    Returns feasibility, actual achievable compound, temperature, and recommendations.
    """
    density_key = None if density is None else round(float(density), 6)
    heat_key = None if specific_heat is None else round(float(specific_heat), 6)
    return _predict_material_synthesis_cached(
        str(base_material).strip(),
        str(target_material).strip(),
        density_key,
        heat_key,
    )


def _predict_material_synthesis_uncached(base_material, target_material, density=None, specific_heat=None):
    try:
        resources = _load_models()
        feasibility_model = resources["feasibility_model"]
        le_pair = resources["pair_encoder"]
        temp_model = resources["temperature_model"]
        transformation_map = resources["transformation_map"]
        compound_model = resources["compound_model"]
        le_compound = resources["compound_encoder"]

        base_material = normalize_material_name(base_material)
        target_material = normalize_material_name(target_material)

        base_mat_lower = base_material.lower()
        target_mat_lower = target_material.lower()

        # 1. CHECK TRANSFORMATION MAP FIRST (O(1) indexed lookup)
        found_match = _transformation_index().get((base_mat_lower, target_mat_lower))

        if found_match is not None:
            trans_info = found_match

            if not trans_info["is_feasible"]:
                return {
                    "success": False,
                    "feasible": False,
                    "base_material": base_material,
                    "target_material": target_material,
                    "message": f"Direct transformation from {base_material} to {target_material} is NOT physically feasible.",
                    "reason": "These materials have incompatible crystal structures and atomic properties.",
                    "recommendations": get_alternatives(
                        base_material, target_material, transformation_map
                    ),
                }

            return {
                "success": True,
                "feasible": True,
                "base_material": base_material,
                "target_material": target_material,
                "achievable_compound": trans_info["target_compound"],
                "required_temperature_c": trans_info["required_temp"],
                "confidence_pct": trans_info["confidence"],
                "instructions": format_synthesis_instructions(
                    base_material,
                    trans_info["target_compound"],
                    trans_info["required_temp"],
                    trans_info["notes"],
                ),
                "notes": trans_info["notes"],
            }
        
        # 2. If not in map, try predictive models
        if density is None or specific_heat is None:
            # Try to get from mendeleev
            try:
                base_elem = element(base_material)
                density = base_elem.density
                specific_heat = 385  # Default value
            except:
                return {
                    "success": False,
                    "error": f"Cannot determine material properties for {base_material}. Please provide density and specific_heat.",
                    "required_params": ["density", "specific_heat"]
                }
        
        # Prepare input for prediction
        material_pair = f"{base_mat_lower}_to_{target_mat_lower}"
        try:
            material_pair_encoded = le_pair.transform([material_pair])[0]
        except:
            # If not seen during training, use a default value
            material_pair_encoded = 0
        
        X_input = pd.DataFrame({
            'density_g_cm3': [density],
            'specific_heat_j_kg_k': [specific_heat],
            'material_pair': [material_pair_encoded]
        })
        
        # 3. Predict feasibility
        feasibility_pred = feasibility_model.predict(X_input)[0]
        feasibility_prob = feasibility_model.predict_proba(X_input)[0]
        
        if feasibility_pred == 0:
            return {
                "success": False,
                "feasible": False,
                "base_material": base_material,
                "target_material": target_material,
                "feasibility_confidence": round(float(max(feasibility_prob)), 2),
                "message": f"AI predicts transformation from {base_material} to {target_material} is NOT feasible.",
                "reason": "Material compatibility analysis suggests this transformation is not achievable under normal synthesis conditions.",
                "recommendations": get_alternatives(base_material, target_material, transformation_map)
            }
        
        # 4. If feasible, predict the compound (if model exists)
        target_compound = target_material  # Default
        if compound_model and le_compound:
            try:
                compound_pred_idx = compound_model.predict(X_input)[0]
                target_compound = le_compound.inverse_transform([compound_pred_idx])[0]
            except:
                pass
        
        # 5. Predict temperature
        predicted_temp = temp_model.predict(X_input)[0]
        
        return {
            "success": True,
            "feasible": True,
            "base_material": base_material,
            "target_material": target_material,
            "achievable_compound": target_compound,
            "required_temperature_c": round(float(predicted_temp), 1),
            "confidence_pct": round(float(feasibility_prob[1]) * 100, 2),
            "instructions": format_synthesis_instructions(
                base_material,
                target_compound,
                predicted_temp,
                f"Transformation via {target_compound} phase"
            ),
            "note": "This is an AI prediction based on material properties"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Prediction error: {str(e)}",
            "type": type(e).__name__
        }


def format_synthesis_instructions(base_material, target_compound, temperature, notes):
    """Format synthesis instructions for the user"""
    return {
        "step_1": f"Prepare {base_material} as base material",
        "step_2": f"Heat to {temperature:.0f}°C in a controlled furnace environment",
        "step_3": f"Maintain temperature to facilitate formation of {target_compound}",
        "step_4": f"Cool gradually to room temperature",
        "result": f"Expected product: {target_compound}",
        "process_notes": notes
    }


def get_alternatives(base_material, target_material, transformation_map):
    """Suggest feasible alternative transformations"""
    alternatives = []
    
    base_key = base_material.lower()
    target_key = target_material.lower()
    
    # Find all feasible transformations FROM the base material
    for trans_key, trans_info in transformation_map.items():
        if trans_info['is_feasible']:
            parts = trans_key.split('_to_')
            if len(parts) == 2 and parts[0] == base_key:
                alternatives.append({
                    "possible_target": parts[1].upper(),
                    "achievable_product": trans_info['target_compound'],
                    "temperature_c": trans_info['required_temp'],
                    "confidence": trans_info['confidence']
                })
    
    return alternatives[:5]  # Top 5 alternatives


# Quick test
if __name__ == "__main__":
    # Test 1: Infeasible transformation (zinc to iron)
    print("=" * 60)
    print("TEST 1: Zinc to Iron (Should be INFEASIBLE)")
    print("=" * 60)
    result = predict_material_synthesis("Zn", "Fe")
    import json
    print(json.dumps(result, indent=2))
    
    # Test 2: Feasible transformation (zinc to brass)
    print("\n" + "=" * 60)
    print("TEST 2: Zinc to Brass (Should be FEASIBLE)")
    print("=" * 60)
    result = predict_material_synthesis("Zn", "Cu")
    print(json.dumps(result, indent=2))
    
    # Test 3: Self transformation (iron to steel)
    print("\n" + "=" * 60)
    print("TEST 3: Iron to Steel (Should be FEASIBLE)")
    print("=" * 60)
    result = predict_material_synthesis("Fe", "Steel")
    print(json.dumps(result, indent=2))
