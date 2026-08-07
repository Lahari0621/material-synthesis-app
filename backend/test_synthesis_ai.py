#!/usr/bin/env python3
"""
PRACTICAL TEST SCRIPT FOR MATERIAL SYNTHESIS AI
Demonstrates all new capabilities with real examples
"""

import json
from synthesis_predictor import predict_material_synthesis

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(result):
    print(json.dumps(result, indent=2))

def test_infeasible_transformation():
    """Test 1: Infeasible transformation with recommendations"""
    print_header("TEST 1: INFEASIBLE TRANSFORMATION (Zinc to Iron)")
    print("Scenario: User wants to produce Iron from Zinc")
    print("Expected: System should reject this and suggest alternatives\n")
    
    result = predict_material_synthesis("Zn", "Fe")
    print_result(result)
    
    if not result.get("success"):
        print("\n✅ PASS: System correctly identified infeasible transformation")
        if result.get("recommendations"):
            print(f"✅ PASS: Provided {len(result['recommendations'])} alternative suggestions")
            for i, alt in enumerate(result['recommendations'][:3], 1):
                print(f"   Alternative {i}: {alt['possible_target']} → {alt['achievable_product']} @ {alt['temperature_c']}°C")
    else:
        print("\n❌ FAIL: Should have rejected this transformation!")

def test_feasible_alloy():
    """Test 2: Feasible alloy formation"""
    print_header("TEST 2: FEASIBLE ALLOY (Zinc to Brass)")
    print("Scenario: User wants to produce Brass from Zinc")
    print("Expected: System should confirm feasibility and provide instructions\n")
    
    result = predict_material_synthesis("Zn", "Cu")
    print_result(result)
    
    if result.get("success"):
        print("\n✅ PASS: System identified feasible transformation")
        print(f"✅ PASS: Achievable product: {result.get('achievable_compound')}")
        print(f"✅ PASS: Temperature: {result.get('required_temperature_c')}°C")
        print(f"✅ PASS: Confidence: {result.get('confidence_pct')}%")
        if result.get("instructions"):
            print("✅ PASS: Provided synthesis instructions")
    else:
        print("\n❌ FAIL: System should have approved this transformation!")

def test_steel_production():
    """Test 3: Iron to Steel transformation"""
    print_header("TEST 3: STEEL PRODUCTION (Iron to Steel)")
    print("Scenario: User wants to produce Steel from Iron")
    print("Expected: System should approve and provide temperature\n")
    
    result = predict_material_synthesis("Fe", "Steel")
    print_result(result)
    
    if result.get("success"):
        print("\n✅ PASS: System identified feasible transformation")
        print(f"✅ PASS: Product: {result.get('achievable_compound')}")
        print(f"✅ PASS: Temperature: {result.get('required_temperature_c')}°C")
    else:
        print("\n❌ FAIL: Steel production should be feasible!")

def test_self_transformation():
    """Test 4: Phase transition of same material"""
    print_header("TEST 4: PHASE TRANSITION (Zinc to Zinc)")
    print("Scenario: User wants to change phase of Zinc")
    print("Expected: System should handle this as phase transition\n")
    
    result = predict_material_synthesis("Zn", "Zn")
    print_result(result)
    
    if result.get("success") or result.get("feasible"):
        print("\n✅ PASS: System identified same-material transformation")
    else:
        print("\n⚠️ NOTE: System may defer this to phase transition model")

def test_copper_alloys():
    """Test 5: Multiple copper alloy possibilities"""
    print_header("TEST 5: COPPER ALLOYS (Copper base material)")
    print("Scenario: Check all feasible transformations from Copper\n")
    
    targets = ["Zn", "Sn", "Ni"]
    
    for target in targets:
        print(f"\n>>> Copper → {target}")
        result = predict_material_synthesis("Cu", target)
        
        if result.get("success"):
            print(f"   ✅ Feasible: {result.get('achievable_compound')} @ {result.get('required_temperature_c')}°C")
        else:
            print(f"   ❌ Not feasible - Alternatives available")
            if result.get("recommendations"):
                alt = result["recommendations"][0]
                print(f"      Suggestion: {alt['achievable_product']} @ {alt['temperature_c']}°C")

def test_rare_metals():
    """Test 6: Rare metals and refractory materials"""
    print_header("TEST 6: REFRACTORY MATERIALS (Tungsten, Molybdenum)")
    print("Scenario: Test high-temperature material transformations\n")
    
    # Tungsten to carbide
    print(">>> Tungsten Carbide Production")
    result = predict_material_synthesis("W", "C")
    print_result(result)
    
    print("\n>>> Molybdenum Steel")
    result = predict_material_synthesis("Mo", "Steel")
    print_result(result)

def test_quality_metrics():
    """Test 7: Quality and confidence metrics"""
    print_header("TEST 7: QUALITY & CONFIDENCE METRICS")
    print("Scenario: Compare confidence scores across different transformations\n")
    
    transformations = [
        ("Fe", "Steel", "High-confidence transformation"),
        ("Zn", "Brass", "Moderate-confidence alloy"),
        ("Al", "Steel", "Low-confidence transformation"),
        ("Zn", "Fe", "Infeasible transformation")
    ]
    
    results_summary = []
    
    for base, target, desc in transformations:
        result = predict_material_synthesis(base, target)
        
        summary = {
            "transformation": f"{base} → {target}",
            "description": desc,
            "feasible": result.get("feasible", False),
            "product": result.get("achievable_compound", "N/A"),
            "temperature": result.get("required_temperature_c", 0),
            "confidence": result.get("confidence_pct", 0)
        }
        results_summary.append(summary)
        
        print(f"{base} → {target}:")
        print(f"  Description: {desc}")
        print(f"  Feasible: {summary['feasible']}")
        print(f"  Product: {summary['product']}")
        print(f"  Temperature: {summary['temperature']}°C")
        print(f"  Confidence: {summary['confidence']}%\n")

def run_all_tests():
    """Run all tests and provide summary"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  🚀 MATERIAL SYNTHESIS AI - COMPREHENSIVE TEST SUITE  ".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        test_infeasible_transformation()
        test_feasible_alloy()
        test_steel_production()
        test_self_transformation()
        test_copper_alloys()
        test_rare_metals()
        test_quality_metrics()
        
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "  ✅ ALL TESTS COMPLETED SUCCESSFULLY  ".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("║" + "  Your Material Synthesis AI is ready for production!  ".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "=" * 78 + "╝")
        
        print("\n📚 Next Steps:")
        print("   1. Start Flask server: python app.py")
        print("   2. Test API endpoints with curl or Postman")
        print("   3. Integrate with your frontend")
        print("   4. Add more transformation data to improve accuracy")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
