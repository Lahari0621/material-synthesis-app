#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER SETUP SCRIPT FOR MATERIAL SYNTHESIS AI
Trains all models and validates the system
"""

import os
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("=" * 70)
    print(">> MATERIAL SYNTHESIS AI - SETUP & TRAINING")
    print("=" * 70)
    
    # Check if dataset exists
    if not os.path.exists('material_synthesis_dataset.csv'):
        print("ERROR: material_synthesis_dataset.csv not found!")
        return False
    
    print("\nOK - Dataset found: material_synthesis_dataset.csv")
    
    # Train synthesis model
    print("\n" + "=" * 70)
    print("STEP 1: Training Synthesis Model")
    print("=" * 70)
    
    try:
        from synthesis_trainer import train_synthesis_model
        train_synthesis_model()
        print("OK - Synthesis model trained successfully!")
    except Exception as e:
        print(f"ERROR training synthesis model: {e}")
        return False
    
    # Test the predictor
    print("\n" + "=" * 70)
    print("STEP 2: Testing Synthesis Predictor")
    print("=" * 70)
    
    try:
        from synthesis_predictor import predict_material_synthesis
        import json
        
        # Test 1: Infeasible (Zinc to Iron)
        print("\nTEST 1: Zinc to Iron (Should be INFEASIBLE)")
        result1 = predict_material_synthesis("Zn", "Fe")
        print(f"Result: {result1.get('feasible', False)} - {result1.get('message', 'Check recommendations')}")
        if result1.get('recommendations'):
            print(f"Recommendations: {result1['recommendations'][0]['possible_target'] if result1['recommendations'] else 'None'}")
        
        # Test 2: Feasible (Zinc to Brass/Copper alloy)
        print("\nTEST 2: Zinc to Copper (Should suggest Brass)")
        result2 = predict_material_synthesis("Zn", "Cu")
        print(f"Result: {result2.get('feasible', False)}")
        if result2.get('feasible'):
            print(f"Product: {result2.get('achievable_compound')}")
            print(f"Temperature: {result2.get('required_temperature_c')}°C")
        
        # Test 3: Feasible (Iron to Steel)
        print("\nTEST 3: Iron to Steel (Should be FEASIBLE)")
        result3 = predict_material_synthesis("Fe", "Steel")
        print(f"Result: {result3.get('feasible', False)}")
        if result3.get('feasible'):
            print(f"Product: {result3.get('achievable_compound')}")
            print(f"Temperature: {result3.get('required_temperature_c')}°C")
        
        print("\nOK - All tests completed!")
        
    except Exception as e:
        print(f"ERROR testing predictor: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("OK - SETUP COMPLETE!")
    print("=" * 70)
    print("\nAPI Endpoints ready to use in Flask app:")
    print("   - /api/synthesis/check - Check if transformation is feasible")
    print("   - /api/synthesis/alternatives/<material> - Get feasible alternatives")
    print("   - /api/predict - Full prediction with history tracking")
    print("\nStart the Flask server with: python app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
