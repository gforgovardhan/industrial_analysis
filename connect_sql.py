import pandas as pd
from sqlalchemy import create_engine

# 1. Load the generated CSV (or use the final_df directly if running in the same script)
csv_file = 'iot_telemetry_data.csv'
print(f"Reading {csv_file}...")
df = pd.read_csv(csv_file)

# 2. Database Connection Credentials
# Format: mysql+pymysql://<username>:<password>@<host>:<port>/<database_name>
USER = 'root'
PASSWORD = '12345678'  # <-- Replace with your MySQL password
HOST = 'localhost'
PORT = '3306'
DATABASE = 'iot_analytics'

# 3. Create Connection Engine
engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# 4. Stream the data to MySQL in chunks to avoid memory bottlenecks
print("Writing data to MySQL database...")
df.to_sql(
    name='iot_telemetry', 
    con=engine, 
    if_exists='append',  # Use 'append' since we already created the table schema
    index=False, 
    chunksize=20000      # Loads 20k rows at a time for stability
)

print("Ingestion complete. Data is now in your MySQL database!")