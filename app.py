import streamlit as st
import matplotlib.pyplot as plt
from utils.scenarios import generate_stadium_load_profile
from models.optimizer import run_bess_optimization
import json

plt.style.use('dark_background')
st.set_page_config(page_title="Bernabéu BESS Optimizer", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

st.title("🏟️ Santiago Bernabéu BESS Financial & Energy Dashboard")
st.markdown("Bankable valuation platform for 70/30 debt-to-equity financing structure.")

st.sidebar.header("Configuration Panel")
scenario = st.sidebar.selectbox("Operating Scenario", ["Concert / Mega Event Day", "Match Day", "Non-Event Day"])
power_rating = st.sidebar.slider("BESS Power Rating (MW)", 2.0, 15.0, 5.0, 0.5)
energy_capacity = st.sidebar.slider("BESS Energy Capacity (MWh)", 4.0, 30.0, 10.0, 1.0)

# Load data and run optimization
df_load = generate_stadium_load_profile(scenario)
load_vector = df_load['Load_MW'].values

market_params = {"base_price": 80.0, "peak_price": 180.0, "demand_charge": 35.0}
results = run_bess_optimization(load_vector, market_params, power_rating, energy_capacity)

# Display Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Original Peak Load", f"{max(load_vector):.1f} MW")
col2.metric("Optimized Peak Grid Draw", f"{results['Peak_Grid_MW']:.1f} MW", delta=f"-{(max(load_vector) - results['Peak_Grid_MW']):.1f} MW", delta_color="inverse")
col3.metric("Daily Cost Savings", f"{results['Daily_Savings']:,.2f} EUR")
col4.metric("Projected Annual Savings", f"{results['Annual_Savings']:,.2f} EUR", delta="Bankable")

# Plotting
st.subheader(f"24-Hour Power Dispatch ({scenario})")
fig, ax = plt.subplots(figsize=(10, 4.5), facecolor='#0e1117')
ax.set_facecolor('#0e1117')
ax.plot(df_load['Timestamp'], load_vector, label="Original Stadium Load", color="#ff4b4b", linestyle="--", linewidth=2)
ax.plot(df_load['Timestamp'], results['Optimized_Load'], label="Optimized Grid Draw (Peak Shaved)", color="#00ff7f", linewidth=2)
ax.set_ylabel("Power [MW]", color='white', fontsize=12)
ax.tick_params(colors='white')
ax.grid(True, color='#333333', linestyle='--')
ax.legend(loc="upper left", facecolor='#161b22', edgecolor='none')
st.pyplot(fig)
