import os
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from models.financials import calculate_bankable_financials
from models.optimizer import run_bess_optimization
from utils.scenarios import generate_stadium_load_profile

# Set up Streamlit page configuration
st.set_page_config(
    page_title="Bernabéu BESS Bankable Dashboard", layout="wide"
)

# Apply custom dark theme styling
st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #00ff7f !important; }
    .stMarkdown p { color: #e6edf3; }
    .zone-card { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 20px; }
    </style>
""",
    unsafe_allow_html=True,
)

# Dashboard Title and Subtitle
st.title("🏟️ Santiago Bernabéu BESS Financial & Energy Dashboard")
st.markdown(
    "Bankable valuation platform for 70/30 debt-to-equity financing structure."
)

# Define stadium zones and their load multiplier characteristics
zone_mapping = {
    "Lateral Oeste (Pº de la Castellana)": {
        "mult": 1.2,
        "desc": (
            "Main grandstand, VIP boxes, heavy HVAC and media load."
        ),
    },
    "Lateral Este (C/ Padre Damián)": {
        "mult": 1.0,
        "desc": (
            "East lateral stand, hospitality lounges, and auxiliary operations."
        ),
    },
    "Fondo Norte (C/ Rafael Salgado)": {
        "mult": 0.9,
        "desc": "North stand, standard seating, and lighting draw.",
    },
    "Fondo Sur (C/ Avda. De Concha Espina)": {
        "mult": 1.1,
        "desc": (
            "South stand, massive crowd surge capacity and concourse services."
        ),
    },
}

# Configuration Panel for User Inputs
st.subheader("Configuration Panel")
col1_c, col2_c, col3_c = st.columns(3)
with col1_c:
  selected_stand = st.selectbox(
      "Select Zone / Stand", list(zone_mapping.keys())
  )
with col2_c:
  scenario = st.selectbox(
      "Operating Scenario",
      ["Concert / Mega Event Day", "Match Day", "Non-Event Day"],
  )
with col3_c:
  power_rating = st.slider("BESS Power Rating (MW)", 2.0, 15.0, 5.0, 0.5)

energy_capacity = st.slider("BESS Energy Capacity (MWh)", 4.0, 30.0, 10.0, 1.0)

current_zone = zone_mapping[selected_stand]

# Display active zone details card
st.markdown(
    f"""
<div class="zone-card">
    <h4>📍 Active Zone: {selected_stand}</h4>
    <p><b>Characteristics:</b> {current_zone['desc']}</p>
    <p><b>Load Multiplier:</b> {current_zone['mult']}x</p>
</div>
""",
    unsafe_allow_html=True,
)

# Display Stadium Layout Image if available in the repository
layout_path = "bernebeu_layout.png"
if os.path.exists(layout_path):
  st.subheader("Stadium Layout & Zone Mapping")
  st.image(
      Image.open(layout_path),
      caption="Santiago Bernabéu Layout & BESS Zones",
      use_container_width=True,
  )

# Generate load profiles and run optimization engine
df_load = generate_stadium_load_profile(scenario)
load_vector = df_load["Load_MW"].values * current_zone["mult"]

market_params = {"base_price": 80.0, "peak_price": 180.0, "demand_charge": 35.0}
results = run_bess_optimization(
    load_vector, market_params, power_rating, energy_capacity
)
fin_results = calculate_bankable_financials(results["Annual_Savings"])

# Render operational performance metrics
st.markdown("---")
st.subheader(f"Operational & Financial Performance ({selected_stand})")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Original Peak Load", f"{max(load_vector):.1f} MW")
col2.metric(
    "Optimized Peak Grid Draw",
    f"{results['Peak_Grid_MW']:.1f} MW",
    delta=f"-{(max(load_vector) - results['Peak_Grid_MW']):.1f} MW",
    delta_color="inverse",
)
col3.metric("Daily Cost Savings", f"{results['Daily_Savings']:,.2f} EUR")
col4.metric(
    "Projected Annual Savings",
    f"{results['Annual_Savings']:,.2f} EUR",
    delta="Bankable",
)

# Render financial feasibility and capital structure metrics
fcol1, fcol2, fcol3, fcol4 = st.columns(4)
fcol1.metric("Total Project CAPEX", f"{fin_results['Total_Capex_EUR']:,.0f} EUR")
fcol2.metric("Bank Debt (70%)", f"{fin_results['Debt_70_Percent_EUR']:,.0f} EUR")
fcol3.metric("Equity (30%)", f"{fin_results['Equity_30_Percent_EUR']:,.0f} EUR")
fcol4.metric(
    "DSCR (Coverage Ratio)",
    f"{fin_results['DSCR']:.2f}x",
    delta="Safe (>1.25)" if fin_results["DSCR"] >= 1.25 else "Check",
)

# Plot 24-hour power dispatch and peak shaving curves
st.subheader(f"24-Hour Power Dispatch ({scenario})")
fig, ax = plt.subplots(figsize=(10, 4), facecolor="#0e1117")
ax.set_facecolor("#0e1117")
ax.plot(
    df_load["Timestamp"],
    load_vector,
    label="Original Stadium Load",
    color="#ff4b4b",
    linestyle="--",
    linewidth=2,
)
ax.plot(
    df_load["Timestamp"],
    results["Optimized_Load"],
    label="Optimized Grid Draw (Peak Shaved)",
    color="#00ff7f",
    linewidth=2,
)
ax.set_ylabel("Power [MW]", color="white", fontsize=12)
ax.tick_params(colors="white")
ax.grid(True, color="#333333", linestyle="--")
ax.legend(loc="upper left", facecolor="#161b22", edgecolor="none")
st.pyplot(fig)
