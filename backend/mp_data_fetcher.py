import os
import pandas as pd
import numpy as np
from mp_api.client import MPRester

def fetch_advanced_materials_data():
    print("🚀 Connecting to Next-Gen Materials Project API...")
    
    # Using your working key!
    os.environ["MP_API_KEY"] = "3IKT5uLzyqbpiEo7TwOxOxmvQviDUMOo"

    dataset = []

    try:
        with MPRester() as mpr:
            print("✔ Connected! Querying advanced crystal structures...")
            
            # --- UPGRADE: Added "symmetry" to the requested fields ---
            docs = mpr.summary.search(
                is_stable=True, 
                fields=["material_id", "formula_pretty", "density", "formation_energy_per_atom", "symmetry"],
                num_chunks=20,
                chunk_size=100
            )
            
            print(f"✔ Downloaded {len(docs)} materials. Processing phase data...")

            for doc in docs:
                name = doc.formula_pretty
                density = doc.density 
                form_energy = abs(doc.formation_energy_per_atom) if doc.formation_energy_per_atom else 0.1
                
                # Extract the exact crystal system (e.g., "Hexagonal", "Cubic")
                crystal_system = str(doc.symmetry.crystal_system) if doc.symmetry else "amorphous"

                simulated_melting_point = 500 + (form_energy * 450)
                simulated_specific_heat = 1000 / (density + 0.1) * 2.5 

                # --- RECORD 1: THE LIQUID PHASE (High Temp Melting) ---
                dataset.append({
                    'base_material': name.lower(),
                    'target_phase': 'liquid',
                    'density_g_cm3': round(density, 2),
                    'specific_heat_j_kg_k': round(simulated_specific_heat, 1),
                    'required_temp_c': round(simulated_melting_point + 50.0, 1)
                })

                # --- RECORD 2: THE SOLID-STATE PHASE (Low Temp Microwave Synthesis) ---
                # Crystal synthesis usually happens at roughly 40% to 60% of the melting point
                synthesis_temp = simulated_melting_point * np.random.uniform(0.4, 0.6)
                
                dataset.append({
                    'base_material': name.lower(),
                    'target_phase': crystal_system.lower(), # e.g., 'hexagonal'
                    'density_g_cm3': round(density, 2),
                    'specific_heat_j_kg_k': round(simulated_specific_heat, 1),
                    'required_temp_c': round(synthesis_temp, 1)
                })

            df = pd.DataFrame(dataset)
            
            # Clean up outliers
            df = df[(df['required_temp_c'] > 0) & (df['required_temp_c'] < 4000)]
            df = df[(df['density_g_cm3'] > 0) & (df['density_g_cm3'] < 25)]

            # Save to our new advanced CSV
            df.to_csv('advanced_material_properties.csv', index=False)
            
            print(f"✅ Success! {len(df)} advanced phase records saved to 'advanced_material_properties.csv'.")

    except Exception as e:
        print(f"❌ Error connecting to API: {e}")

if __name__ == "__main__":
    fetch_advanced_materials_data()