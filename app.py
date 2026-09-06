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
    .zone-card { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("🏟️ Santiago Bernabéu Interactive Zone Explorer")
st.markdown("Interactive Stand Analysis & BESS Peak Shaving Model")

col_map, col_controls = st.columns([1.2, 1])

with col_map:
    st.subheader("Stadium Layout (Click a Stand to Inspect)")
    try:
        img = Image.open("bernabeu_layout.png")
        # Get coordinates when clicking on specific stands in the image
        coords = streamlit_image_coordinates(img, key="bernabeu_map", width=500)
    except FileNotFoundError:
        st.error("⚠️ 'bernabeu_layout.png' not found.")
        coords = None

# Default zone mapping based on image quadrants or direct selection
selected_stand = "Lateral Oeste (Pº de la Castellana)"

if coords is not None:
    x, y = coords["x"], coords["y"]
    # Map pixel coordinates roughly based on the Bernabeu image layout
    # Assuming standard dimensions of the uploaded image
    if y < 150:
        selected_stand = "Lateral Oeste (Pº de la Castellana)"
    elif y > 350:
        selected_stand = "Lateral Este (C/ Padre Damián)"
    elif x < 200:
        selected_stand = "Fondo Sur (C/ Avda. De Concha Espina)"
    else:
        selected_stand = "Fondo Norte (C/ Rafael Salgado)"

with col_controls:
    st.subheader("Zone Diagnostic Panel")
    
    # Allow manual override via dropdown as well
    selected_stand = st.selectbox(
        "Active Stand / Zone (or click on map)", 
        [
            "Lateral Oeste (Pº de la Castellana)",
            "Lateral Este (C/ Padre Damián)",
            "Fondo Norte (C/ Rafael Salgado)",
            "Fondo Sur (C/ Avda. De Concha Espina)"
        ],
        index=["Lateral Oeste (Pº de la Castellana)", "Lateral Este (C/ Padre Damián)", "Fondo Norte (C/ Rafael Salgado)", "Fondo Sur (C/ Avda. De Concha Espina)"].index(selected_stand)
    )

zone_multipliers = {
    "Lateral Oeste (Pº de la Castellana)": {"mult": 1.2, "desc": "Main grandstand, VIP boxes, heavy HVAC and media load."},
    "Lateral Este (C/ Padre Damián)": {"mult": 1.0, "desc": "East lateral stand, hospitality lounges, and auxiliary operations."},
    "Fondo Norte (C/ Rafael Salgado)": {"mult": 0.9, "desc": "North stand, standard seating, and lighting draw."},
    "Fondo Sur (C/ Avda. De Concha Espina)": {"mult": 1.1, "desc": "South stand, massive crowd surge capacity and concourse services."}
}

current_zone = zone_multipliers[selected_stand]

st.markdown(f"""
<div class="zone-card">
    <h4>📍 Selected Zone: {selected_stand}</h4>
    <p><b>Characteristics:</b> {current_zone['desc']}</p>
    <p><b>Load Multiplier:</b> {current_zone['mult']}x</p>
</div>
""", unsafe_allow_html=True)

# Run simulation based on selected zone
scenario = st.selectbox("Operating Scenario", ["Concert / Mega Event Day", "Match Day", "Non-Event Day"])
df_load = generate_stadium_load_profile(scenario)
load_vector = df_load['Load_MW'].values * current_zone["mult"]

market_params = {"base_price": 80.0, "peak_price": 180.0, "demand_charge": 35.0}
results = run_bess_optimization(load_vector, market_params, 5.0, 10.0)
fin_results = calculate_bankable_financials(results['Annual_Savings'])

st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("Zone Peak Load", f"{max(load_vector):.1f} MW")
col2.metric("Optimized Grid Draw", f"{results['Peak_Grid_MW']:.1f} MW")
col3.metric("Projected Annual Savings", f"{results['Annual_Savings']:,.2f} EUR", delta="Bankable")
