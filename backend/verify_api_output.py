#!/usr/bin/env python3
"""
Comprehensive API Test Suite for Material Synthesis AI
Tests various material pairs to verify accuracy
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_synthesis(base_material, target_material, expected_feasible=None, description=""):
    """Test a material synthesis transformation"""
    
    print("\n" + "=" * 80)
    print(f"TEST: {base_material} → {target_material}")
    if description:
        print(f"Description: {description}")
    print("=" * 80)
    
    try:
        # Test the synthesis check endpoint
        response = requests.post(
            f"{BASE_URL}/api/synthesis/check",
            json={
                "base_material": base_material,
                "target_material": target_material
            }
        )
        
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Feasible: {data.get('feasible', 'N/A')}")
        
        if data.get('feasible'):
            print(f"✅ FEASIBLE")
            print(f"   Product: {data.get('achievable_compound')}")
            print(f"   Temperature: {data.get('required_temperature_c')}°C")
            print(f"   Confidence: {data.get('confidence_pct')}%")
            print(f"   Notes: {data.get('notes')}")
            
            # Show instructions
            instructions = data.get('instructions', {})
            if instructions:
                print("\n   Synthesis Steps:")
                print(f"   1. {instructions.get('step_1')}")
                print(f"   2. {instructions.get('step_2')}")
                print(f"   3. {instructions.get('step_3')}")
                print(f"   4. {instructions.get('step_4')}")
                print(f"   Result: {instructions.get('result')}")
        else:
            print(f"❌ NOT FEASIBLE")
            print(f"   Reason: {data.get('reason')}")
            
            # Show recommendations
            recommendations = data.get('recommendations', [])
            if recommendations:
                print(f"\n   💡 Suggested Alternatives ({len(recommendations)} options):")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"      {i}. {rec.get('possible_target')} → {rec.get('achievable_product')} @ {rec.get('temperature_c')}°C ({rec.get('confidence')}%)")
        
        print(f"\nFull Response:")
        print(json.dumps(data, indent=2))
        
        return data
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  MATERIAL SYNTHESIS AI - API VERIFICATION TEST  ".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    print(f"\nServer: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ========================================
    # TEST CATEGORY 1: INFEASIBLE TRANSFORMATIONS
    # ========================================
    print("\n" + "█" * 80)
    print("█ CATEGORY 1: INFEASIBLE TRANSFORMATIONS (Should be rejected)")
    print("█" * 80)
    
    infeasible_tests = [
        ("Zn", "Fe", False, "Pure Iron cannot be made from Zinc directly"),
        ("Cu", "Al", False, "Copper to Aluminum - inverse order infeasible"),
        ("Pb", "Au", False, "Lead to Gold - impossible without nuclear reaction"),
    ]
    
    infeasible_results = []
    for base, target, expected, desc in infeasible_tests:
        result = test_synthesis(base, target, expected, desc)
        infeasible_results.append({
            "pair": f"{base}→{target}",
            "expected": "Not Feasible",
            "actual": "Not Feasible" if not result.get('feasible') else "Feasible",
            "correct": not result.get('feasible')
        })
    
    # ========================================
    # TEST CATEGORY 2: FEASIBLE ALLOY FORMATION
    # ========================================
    print("\n" + "█" * 80)
    print("█ CATEGORY 2: FEASIBLE ALLOY FORMATION (Should be approved)")
    print("█" * 80)
    
    feasible_tests = [
        ("Zn", "Cu", True, "Zinc + Copper = Brass (very common)"),
        ("Cu", "Sn", True, "Copper + Tin = Bronze (ancient alloy)"),
        ("Cu", "Zn", True, "Copper + Zinc = Brass (reverse direction)"),
        ("Fe", "Ni", True, "Iron + Nickel = Nickel Steel"),
        ("Al", "Mg", True, "Aluminum + Magnesium = Lightweight Alloy"),
    ]
    
    feasible_results = []
    for base, target, expected, desc in feasible_tests:
        result = test_synthesis(base, target, expected, desc)
        feasible_results.append({
            "pair": f"{base}→{target}",
            "expected": "Feasible",
            "actual": "Feasible" if result.get('feasible') else "Not Feasible",
            "product": result.get('achievable_compound', 'N/A'),
            "temperature": result.get('required_temperature_c', 0),
            "correct": result.get('feasible') == expected
        })
    
    # ========================================
    # TEST CATEGORY 3: SAME MATERIAL (PHASE TRANSITIONS)
    # ========================================
    print("\n" + "█" * 80)
    print("█ CATEGORY 3: SAME MATERIAL - PHASE TRANSITIONS")
    print("█" * 80)
    
    phase_tests = [
        ("Fe", "Fe", True, "Iron to Iron - phase transition"),
        ("Zn", "Zn", True, "Zinc to Zinc - phase transition"),
        ("Cu", "Cu", True, "Copper to Copper - phase transition"),
        ("Al", "Al", True, "Aluminum to Aluminum - phase transition"),
    ]
    
    phase_results = []
    for base, target, expected, desc in phase_tests:
        result = test_synthesis(base, target, expected, desc)
        phase_results.append({
            "pair": f"{base}→{target}",
            "expected": "Feasible",
            "actual": "Feasible" if result.get('feasible') else "Not Feasible",
            "product": result.get('achievable_compound', 'N/A'),
            "correct": result.get('feasible') == expected
        })
    
    # ========================================
    # TEST CATEGORY 4: STEEL & HIGH-TECH ALLOYS
    # ========================================
    print("\n" + "█" * 80)
    print("█ CATEGORY 4: STEEL & ADVANCED ALLOYS")
    print("█" * 80)
    
    advanced_tests = [
        ("Fe", "Steel", True, "Iron to Steel - add carbon"),
        ("Mo", "Steel", True, "Molybdenum Steel - tool steel"),
        ("W", "Mo", True, "Tungsten-Molybdenum alloy - high temp"),
        ("Ti", "Al", True, "Titanium-Aluminum alloy"),
    ]
    
    advanced_results = []
    for base, target, expected, desc in advanced_tests:
        result = test_synthesis(base, target, expected, desc)
        advanced_results.append({
            "pair": f"{base}→{target}",
            "expected": "Feasible",
            "actual": "Feasible" if result.get('feasible') else "Not Feasible",
            "product": result.get('achievable_compound', 'N/A'),
            "temperature": result.get('required_temperature_c', 0),
            "correct": result.get('feasible') == expected
        })
    
    # ========================================
    # TEST CATEGORY 5: COMMON INDUSTRIAL TRANSFORMATIONS
    # ========================================
    print("\n" + "█" * 80)
    print("█ CATEGORY 5: COMMON INDUSTRIAL TRANSFORMATIONS")
    print("█" * 80)
    
    industrial_tests = [
        ("Pb", "Sn", True, "Lead-Tin Solder"),
        ("Sn", "Cu", True, "Bronze creation"),
        ("Ni", "Cr", True, "Nickel-Chromium - stainless base"),
        ("Mg", "Zn", True, "Magnesium-Zinc lightweight"),
    ]
    
    industrial_results = []
    for base, target, expected, desc in industrial_tests:
        result = test_synthesis(base, target, expected, desc)
        industrial_results.append({
            "pair": f"{base}→{target}",
            "expected": "Feasible",
            "actual": "Feasible" if result.get('feasible') else "Not Feasible",
            "product": result.get('achievable_compound', 'N/A'),
            "correct": result.get('feasible') == expected
        })
    
    # ========================================
    # SUMMARY REPORT
    # ========================================
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  VERIFICATION SUMMARY  ".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝\n")
    
    print("CATEGORY 1: INFEASIBLE TRANSFORMATIONS")
    print("-" * 80)
    for test in infeasible_results:
        status = "✅ PASS" if test['correct'] else "❌ FAIL"
        print(f"{status} | {test['pair']:10} | Expected: {test['expected']:12} | Got: {test['actual']}")
    correct_1 = sum(1 for t in infeasible_results if t['correct'])
    print(f"Score: {correct_1}/{len(infeasible_results)}\n")
    
    print("CATEGORY 2: FEASIBLE ALLOY FORMATION")
    print("-" * 80)
    for test in feasible_results:
        status = "✅ PASS" if test['correct'] else "❌ FAIL"
        print(f"{status} | {test['pair']:10} | Product: {test['product']:20} | Temp: {test['temperature']:6.0f}°C")
    correct_2 = sum(1 for t in feasible_results if t['correct'])
    print(f"Score: {correct_2}/{len(feasible_results)}\n")
    
    print("CATEGORY 3: PHASE TRANSITIONS")
    print("-" * 80)
    for test in phase_results:
        status = "✅ PASS" if test['correct'] else "❌ FAIL"
        print(f"{status} | {test['pair']:10} | Product: {test['product']:20} | {test['actual']}")
    correct_3 = sum(1 for t in phase_results if t['correct'])
    print(f"Score: {correct_3}/{len(phase_results)}\n")
    
    print("CATEGORY 4: ADVANCED ALLOYS")
    print("-" * 80)
    for test in advanced_results:
        status = "✅ PASS" if test['correct'] else "❌ FAIL"
        print(f"{status} | {test['pair']:10} | Product: {test['product']:20} | Temp: {test['temperature']:6.0f}°C")
    correct_4 = sum(1 for t in advanced_results if t['correct'])
    print(f"Score: {correct_4}/{len(advanced_results)}\n")
    
    print("CATEGORY 5: INDUSTRIAL TRANSFORMATIONS")
    print("-" * 80)
    for test in industrial_results:
        status = "✅ PASS" if test['correct'] else "❌ FAIL"
        print(f"{status} | {test['pair']:10} | Product: {test['product']:20} | {test['actual']}")
    correct_5 = sum(1 for t in industrial_results if t['correct'])
    print(f"Score: {correct_5}/{len(industrial_results)}\n")
    
    # ========================================
    # OVERALL SCORE
    # ========================================
    total_tests = len(infeasible_results) + len(feasible_results) + len(phase_results) + len(advanced_results) + len(industrial_results)
    total_correct = correct_1 + correct_2 + correct_3 + correct_4 + correct_5
    accuracy = (total_correct / total_tests * 100) if total_tests > 0 else 0
    
    print("=" * 80)
    print(f"OVERALL ACCURACY: {total_correct}/{total_tests} ({accuracy:.1f}%)")
    print("=" * 80)
    
    if accuracy >= 90:
        print("✅ AI VERIFICATION: EXCELLENT - Ready for Production")
    elif accuracy >= 75:
        print("🟡 AI VERIFICATION: GOOD - Minor improvements needed")
    elif accuracy >= 60:
        print("⚠️  AI VERIFICATION: FAIR - Needs attention")
    else:
        print("❌ AI VERIFICATION: POOR - Requires retraining")
    
    print("\n" + "=" * 80)
    print("Test completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
