# %% [markdown]
# # Step 1: Database Connection & Libraries
# Run this cell first to import libraries and connect to MySQL.

# %%
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sqlalchemy import create_engine

USER = 'root'
PASSWORD = '12345678'  # <-- Replace with your MySQL password
HOST = 'localhost'
PORT = '3306'
DATABASE = 'iot_analytics'

print("Connecting to database...")
engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# Query key metrics to keep execution fast
query = """
SELECT 
    component_type, 
    temperature_celsius, 
    operating_voltage, 
    signal_coherence_index 
FROM iot_telemetry;
"""

print("Loading data from MySQL into Pandas...")
df = pd.read_sql(query, con=engine)
print(f"Data loaded. Total rows: {df.shape[0]:,}")

# %% [markdown]
# # Step 2: Correlation Analysis
# This cell calculates the mathematical relationships between the metrics and plots a heatmap.

# %%
print("Running Correlation Analysis...")
correlation_matrix = df[['temperature_celsius', 'operating_voltage', 'signal_coherence_index']].corr()
print(correlation_matrix)

# Plot heatmap directly inside VS Code
plt.figure(figsize=(7, 5))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
plt.title('Hardware Telemetry Metric Correlations')
plt.tight_layout()
plt.show() # This will render the plot in your VS Code panel

# %% [markdown]
# # Step 3: Outlier Detection
# This cell checks temperature data for anomalies across component types using the Interquartile Range (IQR).

# %%
print("Running Outlier Detection...")

for component in df['component_type'].unique():
    comp_data = df[df['component_type'] == component]['temperature_celsius']
    
    Q1 = comp_data.quantile(0.25)
    Q3 = comp_data.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = comp_data[(comp_data < lower_bound) | (comp_data > upper_bound)]
    percentage = (len(outliers) / len(comp_data)) * 100
    
    print(f"{component}: Detected {len(outliers):,} outliers ({percentage:.2f}% of readings)")

# Render boxplot
plt.figure(figsize=(9, 5))
sns.boxplot(x='component_type', y='temperature_celsius', data=df, palette='Set2')
plt.title('Temperature Distributions & Statistical Outliers by Component')
plt.xlabel('Component Type')
plt.ylabel('Temperature (°C)')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# %% [markdown]
# # Step 4: Hypothesis Testing
# This cell mathematically tests whether higher temperatures significantly degrade signal performance.

# %%
print("Executing Hypothesis Testing...")
# We use Pearson's correlation test
r_val, p_val = stats.pearsonr(df['temperature_celsius'], df['signal_coherence_index'])

print(f"Pearson Correlation Coefficient (r): {r_val:.4f}")
print(f"P-value: {p_val}")

if p_val < 0.05:
    print("Result: Statistically Significant (p < 0.05).")
    print("We reject the Null Hypothesis. There is a verified negative relationship between temperature and signal coherence.")
else:
    print("Result: Not Statistically Significant.")