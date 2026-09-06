import numpy as np
import pandas as pd

def generate_stadium_load_profile(scenario_name="Concert / Mega Event Day"):
    """
    Generate 24-hour load profiles (15-minute intervals, 96 steps) 
    for Santiago Bernabéu stadium operating scenarios.
    """
    time_index = pd.date_range(start="2026-06-09 00:00:00", periods=96, freq="15min")
    base_load = np.full(96, 1.0)
    
    if scenario_name == "Concert / Mega Event Day":
        load_series = base_load.copy()
        load_series[56:92] = np.linspace(1.0, 9.0, 36) # Peak up to 9 MW during event
    elif scenario_name == "Match Day":
        load_series = base_load.copy()
        load_series[60:88] = np.linspace(1.0, 5.5, 28) # Peak up to 5.5 MW
        load_series[88:92] = 3.5
    else: # Non-Event Day
        load_series = base_load.copy()
        load_series[32:80] += 0.5
        
    df_load = pd.DataFrame({
        'Timestamp': time_index,
        'Load_MW': load_series
    })
    
    return df_load
