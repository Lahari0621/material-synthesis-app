import pandas as pd
import numpy as np

def generate_synthetic_data():
    print("🧪 Generating synthetic thermodynamic data...")
    # Seed ensures we get the same "random" numbers every time we run it
    np.random.seed(42) 
    num_samples = 500

    # Generate random physical properties for 500 imaginary materials
    melting_points = np.random.uniform(500, 3000, num_samples)  # 500°C to 3000°C
    densities = np.random.uniform(2.0, 20.0, num_samples)       # 2.0 to 20.0 g/cm³
    specific_heats = np.random.uniform(300, 1000, num_samples)  # 300 to 1000 J/kg·K
    target_conversions = np.random.uniform(50.0, 100.0, num_samples) # 50% to 100%

    # The Synthetic Physics Formula: 
    # Required temp scales up with melting point and conversion %
    required_temps = (melting_points * (target_conversions / 100.0)) + (densities * 5) - (specific_heats * 0.1)
    
    # Add random noise (±15 degrees) so it isn't a perfect, easy straight line
    noise = np.random.normal(0, 15, num_samples)
    required_temps += noise

    # Compile into a Pandas DataFrame
    df = pd.DataFrame({
        'melting_point_c': melting_points.round(1),
        'density_g_cm3': densities.round(2),
        'specific_heat_j_kg_k': specific_heats.round(1),
        'target_conversion_pct': target_conversions.round(1),
        'required_temp_c': required_temps.round(1)
    })

    # Save to CSV
    df.to_csv('material_properties_dataset.csv', index=False)
    print("✅ Data saved to 'material_properties_dataset.csv'!")

if __name__ == "__main__":
    generate_synthetic_data()