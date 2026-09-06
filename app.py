import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates
from utils.scenarios import generate_stadium_load_profile
from models.optimizer import run_bess_optimization
from models.financials import calculate_bankable_financials

plt.style.use('dark_background')
st.set_page_config(page_title="Bernabéu BESS Bankable Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

st.title("🏟️ Santiago Bernabéu BESS Financial & Energy Dashboard")
st.markdown("Bankable valuation platform for 70/30 debt-to-equity financing structure.")

col_map, col_controls = st.columns([1.1, 1])

with col_map:
    st.subheader("Stadium Stand Interactive Map")
    try:
        img_path = "bernabeu_layout.png"
        img = Image.open(img_path)
        st.image(img, caption="Santiago Bernabéu Layout", use_container_width=True)
        coords = streamlit_image_coordinates(img, key="bernabeu_map")
    except FileNotFoundError:
        st.error("⚠️ File 'bernabeu_layout.png' not found in root directory.")
        coords = None

with col_controls:
    st.subheader("Configuration Panel")
    scenario = st.selectbox("Operating Scenario", ["Concert / Mega Event Day", "Match Day", "Non-Event Day"])
    power_rating = st.slider("BESS Power Rating (MW)", 2.0, 15.0, 5.0, 0.5)
    energy_capacity = st.slider("BESS Energy Capacity (MWh)", 4.0, 30.0, 10.0, 1.0)
    
    zone_mapping = {
        "Lateral Oeste (Pº de la Castellana)": 1.2,
        "Lateral Este (C/ Padre Damián)": 1.0,
        "Fondo Norte (C/ Rafael Salgado)": 0.9,
        "Fondo Sur (C/ Avda. De Concha Espina)": 1.1
    }
    selected_stand = st.selectbox("Select Zone / Stand", list(zone_mapping.keys()))

df_load = generate_stadium_load_profile(scenario)
load_vector = df_load['Load_MW'].values * zone_mapping[selected_stand]

market_params = {"base_price": 80.0, "peak_price": 180.0, "demand_charge": 35.0}
results = run_bess_optimization(load_vector, market_params, power_rating, energy_capacity)
fin_results = calculate_bankable_financials(results['Annual_Savings'])

st.markdown("---")
st.subheader(f"Operational & Financial Performance ({selected_stand})")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Original Peak Load", f"{max(load_vector):.1f} MW")
col2.metric("Optimized Peak Grid Draw", f"{results['Peak_Grid_MW']:.1f} MW", delta=f"-{(max(load_vector) - results['Peak_Grid_MW']):.1f} MW", delta_color="inverse")
col3.metric("Daily Cost Savings", f"{results['Daily_Savings']:,.2f} EUR")
col4.metric("Projected Annual Savings", f"{results['Annual_Savings']:,.2f} EUR", delta="Bankable")

fcol1, fcol2, fcol3, fcol4 = st.columns(4)
fcol1.metric("Total Project CAPEX", f"{fin_results['Total_Capex_EUR']:,.0f} EUR")
fcol2.metric("Bank Debt (70%)", f"{fin_results['Debt_70_Percent_EUR']:,.0f} EUR")
fcol3.metric("Equity (30%)", f"{fin_results['Equity_30_Percent_EUR']:,.0f} EUR")
fcol4.metric("DSCR (Coverage Ratio)", f"{fin_results['DSCR']:.2f}x", delta="Safe (>1.25)" if fin_results['DSCR'] >= 1.25 else "Check")

st.subheader(f"24-Hour Power Dispatch ({scenario})")
fig, ax = plt.subplots(figsize=(10, 4), facecolor='#0e1117')
ax.set_facecolor('#0e1117')
ax.plot(df_load['Timestamp'], load_vector, label="Original Stadium Load", color="#ff4b4b", linestyle="--", linewidth=2)
ax.plot(df_load['Timestamp'], results['Optimized_Load'], label="Optimized Grid Draw (Peak Shaved)", color="#00ff7f", linewidth=2)
ax.set_ylabel("Power [MW]", color='white', fontsize=12)
ax.tick_params(colors='white')
ax.grid(True, color='#333333', linestyle='--')
ax.legend(loc="upper left", facecolor='#161b22', edgecolor='none')
st.pyplot(fig)
