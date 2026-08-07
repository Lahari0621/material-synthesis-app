import pandas as pd
import mysql.connector

def get_training_data():
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "Chaithu@123",
        "database": "furnace_db"
    }
    
    try:
        conn = mysql.connector.connect(**db_config)
        # Pulling data into a Pandas DataFrame
        query = "SELECT material_name, temp_celsius, conversion_pct FROM material_phases"
        df = pd.read_sql(query, conn)
        conn.close()

        print("✔ Training data loaded from MySQL successfully!")
        print(df.head()) # Shows the first 5 rows to verify
        return df
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

if __name__ == "__main__":
    get_training_data()