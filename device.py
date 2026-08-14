import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Configuration
num_devices = 50
start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 6, 30)
time_step_minutes = 30

# Generate timestamps
timestamps = pd.date_range(start=start_date, end=end_date, freq=f'{time_step_minutes}T')
num_timestamps = len(timestamps)

# Device Metadata
locations = ['North-Region', 'South-Region', 'East-Region', 'West-Region', 'Central-Region']
component_types = ['Microcontroller', 'Transceiver', 'Power_Module']

devices = []
for i in range(1, num_devices + 1):
    devices.append({
        'device_id': f'DEV_{i:03d}',
        'location': np.random.choice(locations),
        'component_type': np.random.choice(component_types, p=[0.4, 0.3, 0.3]),
        # Introduce a baseline wear multiplier for some devices (simulating older hardware)
        'wear_factor': np.random.uniform(1.0, 1.25) if i % 7 == 0 else 1.0
    })

devices_df = pd.DataFrame(devices)

# Generate time-series data
records = []

print("Generating dataset...")
for idx, device in devices_df.iterrows():
    dev_id = device['device_id']
    comp_type = device['component_type']
    wear = device['wear_factor']
    
    # Base metrics depending on component type
    if comp_type == 'Power_Module':
        base_temp = 55.0
        base_volt = 12.0
    elif comp_type == 'Transceiver':
        base_temp = 40.0
        base_volt = 3.3
    else: # Microcontroller
        base_temp = 35.0
        base_volt = 5.0
        
    # Generate continuous metrics using random walks and wave functions
    # Time of day effect on temperature (diurnal cycle)
    hour_values = timestamps.hour.values
    diurnal_effect = np.sin(2 * np.pi * hour_values / 24.0) * 5.0
    
    # Over-time degradation trend (wear increases temperature slightly over 6 months)
    degradation_trend = np.linspace(0, 3.0 * wear, num_timestamps)
    
    # Noise components
    temp_noise = np.random.normal(0, 1.5, num_timestamps)
    volt_noise = np.random.normal(0, 0.05 * base_volt, num_timestamps)
    
    # Compute metrics vectorially for performance
    temperatures = base_temp + diurnal_effect + degradation_trend + temp_noise
    voltages = base_volt - (degradation_trend * 0.02) + volt_noise
    
    # Signal coherence index (0.0 to 1.0) - drops when temperature is very high
    # Transceivers are more prone to signal loss
    signal_base = 0.95 if comp_type != 'Transceiver' else 0.85
    signal_coherence = signal_base - (temperatures - base_temp) * 0.005 - np.random.exponential(0.02, num_timestamps)
    signal_coherence = np.clip(signal_coherence, 0.0, 1.0)
    
    # Generate error flags
    # Trigger an error if temperature crosses critical thresholds or signal is extremely low
    temp_threshold = base_temp + 15.0 * wear
    error_flags = np.where(
        (temperatures > temp_threshold) | (signal_coherence < 0.35) | (np.random.random(num_timestamps) < 0.001), 
        1, 
        0
    )
    
    # Store temporary dataframe for this device
    device_data = pd.DataFrame({
        'timestamp': timestamps,
        'device_id': dev_id,
        'location': device['location'],
        'component_type': comp_type,
        'temperature_celsius': np.round(temperatures, 2),
        'operating_voltage': np.round(voltages, 2),
        'signal_coherence_index': np.round(signal_coherence, 3),
        'error_flag': error_flags
    })
    
    records.append(device_data)

# Concatenate all dataframes
final_df = pd.concat(records, ignore_index=True)

# Save to CSV
output_path = 'iot_telemetry_data.csv'
final_df.to_csv(output_path, index=False)
print(f"Dataset generated successfully with {len(final_df):,} rows.")
print(f"Saved to: {output_path}")