import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from utils.scenarios import generate_stadium_load_profile
from models.optimizer import run_bess_optimization
from models.financials import calculate_bankable_financials

st.set_page_config(page_title="Bernabéu BESS Bankable Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #00ff7f !important; }
    .stMarkdown p { color: #e6edf3; }
    .zone-card { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏟️ Santiago Bernabéu Digital Interactive Map")
st.markdown("Advanced BESS Optimization & 70/30 Financial Model with Zone-Based Digital Mapping.")

# Zone definitions & characteristics
zone_mapping = {
    "Lateral Oeste (Pº de la Castellana)": {"mult": 1.2, "desc": "Main grandstand, VIP boxes, heavy HVAC and media load.", "y_range": (0, 250)},
    "Lateral Este (C/ Padre Damián)": {"mult": 1.0, "desc": "East lateral stand, hospitality lounges, and auxiliary operations.", "y_range": (550, 800)},
    "Fondo Norte (C/ Rafael Salgado)": {"mult": 0.9, "desc": "North stand, standard seating, and lighting draw.", "x_range": (550, 800)},
    "Fondo Sur (C/ Avda. De Concha Espina)": {"mult": 1.1, "desc": "South stand, massive crowd surge capacity and concourse services.", "x_range": (0, 250)}
}

col_map, col_controls = st.columns([1.3, 1])

with col_controls:
    st.subheader("Configuration & Zone Selection")
    
    # Fallback or direct selection dropdown synced with map
    selected_stand = st.selectbox(
        "Select Stadium Zone / Stand:",
        list(zone_mapping.keys())
    )
    
    scenario = st.selectbox("Operating Scenario", ["Concert / Mega Event Day", "Match Day", "Non-Event Day"])
    power_rating = st.slider("BESS Power Rating (MW)", 2.0, 15.0, 5.0, 0.5)
    energy_capacity = st.slider("BESS Energy Capacity (MWh)", 4.0, 30.0, 10.0, 1.0)

with col_map:
    st.subheader("Interactive Digital Stand Map")
    
    try:
        img = Image.open("bernabeu_layout.png")
        width, height = img.size
    except FileNotFoundError:
        st.error("⚠️ 'bernabeu_layout.png' not found.")
        width, height = 800, 800

    # Create Plotly figure with background image and interactive digital zones
    fig = go.Figure()

    # Add Bernabéu layout as background image
    fig.add_layout_image(
        source=img,
        xref="x",
        yref="y",
        x=0,
        y=height,
        sizex=width,
        sizey=height,
        sizing="stretch",
        opacity=0.85,
        layer="below"
    )

    # Define interactive hover regions corresponding to the 4 sides
    zones_coords = [
        {"name": "Lateral Oeste (Pº de la Castellana)", "x": [width*0.2, width*0.8, width*0.8, width*0.2], "y": [height*0.05, height*0.05, height*0.25, height*0.25]},
        {"name": "Lateral Este (C/ Padre Damián)", "x": [width*0.2, width*0.8, width*0.8, width*0.2], "y": [height*0.75, height*0.75, height*0.95, height*0.95]},
        {"name": "Fondo Norte (C/ Rafael Salgado)", "x": [width*0.75, width*0.95, width*0.95, height*0.75], "y": [height*0.2, height*0.2, height*0.8, height*0.8]},
        {"name": "Fondo Sur (C/ Avda. De Concha Espina)", "x": [width*0.05, width*0.25, width*0.25, width*0.05], "y": [height*0.2, height*0.2, height*0.8, height*0.8]}
    ]

    # Add transparent scatter regions for hovering and tooltips
    fig.add_trace(go.Scatter(
        x=[width*0.5, width*0.5, width*0.8, width*0.2],
        y=[height*0.15, height*0.85, height*0.5, height*0.5],
        mode="markers+text",
        text=["Lateral Oeste", "Lateral Este", "Fondo Norte", "Fondo Sur"],
        textposition="top center",
        textfont=dict(color="#00ff7f", size=14, family="Arial Black"),
        marker=dict(size=14, color="#00ff7f", symbol="square", line=dict(width=2, color="white")),
        hoverinfo="text",
        hovertext=[f"<b>{k}</b><br>{v['desc']}" for k, v in zone_mapping.items()]
    ))

    fig.update_xaxes(range=[0, width], showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(range=[height, 0], showgrid=False, zeroline=False, visible=False)
    fig.update_layout(
        width=600,
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        showlegend=False
    )

    # Render interactive map in Streamlit and capture selection/clicks
    event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")

current_zone = zone_mapping[selected_stand]

st.markdown(f"""
<div class="zone-card">
    <h4>📍 Active Zone: {selected_stand}</h4>
    <p><b>Characteristics:</b> {current_zone['desc']}</p>
    <p><b>Load Multiplier:</b> {current_zone['mult']}x</p>
</div>
""", unsafe_allow_html=True)

# Run optimization & financial models
df_load = generate_stadium_load_profile(scenario)
load_vector = df_load['Load_MW'].values * current_zone["mult"]

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
fig_line, ax = plt.subplots(figsize=(10, 4), facecolor='#0e1117')
ax.set_facecolor('#0e1117')
ax.plot(df_load['Timestamp'], load_vector, label="Original Stadium Load", color="#ff4b4b", linestyle="--", linewidth=2)
ax.plot(df_load['Timestamp'], results['Optimized_Load'], label="Optimized Grid Draw (Peak Shaved)", color="#00ff7f", linewidth=2)
ax.set_ylabel("Power [MW]", color='white', fontsize=12)
ax.tick_params(colors='white')
ax.grid(True, color='#333333', linestyle='--')
ax.legend(loc="upper left", facecolor='#161b22', edgecolor='none')
st.pyplot(fig_line)
