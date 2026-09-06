import streamlit as st
import numpy as np
import pandas as pd
import pulp
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

plt.style.use('dark_background')
st.set_page_config(page_title="Bernabéu Interactive Zone Explorer", layout="wide")

st.title("🏟️ Santiago Bernabéu Interactive Zone Explorer")
st.markdown("Click on specific stadium zones to inspect regional load profiles, BESS placement, and sub-system economics.")

# Layout columns: Left for interactive image map, Right for zone details
col_map, col_info = st.columns([1.2, 1])

with col_map:
    st.subheader("Stadium Layout Map")
    # Load a placeholder or stadium image (you can replace with your image path)
    # Here we create a mock schematic image or load one if available
    try:
        img = Image.open("bernabeu_layout.png")
    except:
        # Fallback dummy image representation if file doesn't exist yet
        img = Image.new('RGB', (600, 400), color='#161b22')
    
    # Get coordinates of user click on the image
    coords = streamlit_image_coordinates(img, key="stadium_map")

# Define zone mapping based on image coordinates (assuming 600x400 dimension)
selected_zone = "General Stadium"
if coords is not None:
    x, y = coords["x"], coords["y"]
    # Simple bounding box mapping for zones
    if x < 300 and y < 200:
        selected_zone = "North Stand & Hospitality (High AC Load)"
    elif x >= 300 and y < 200:
        selected_zone = "East Stand & VIP Boxes (Premium Demand)"
    elif x < 300 and y >= 200:
        selected_zone = "South Stand & General Admission (Massive Crowd Surge)"
    else:
        selected_zone = "Subterranean BESS Container Hub (5 MW / 10 MWh LFP)"

with col_info:
    st.subheader("Zone Diagnostic & Analytics")
    st.info(f"Active Selected Zone: **{selected_zone}**")
    
    if "BESS" in selected_zone:
        st.markdown("""
        * **Technology:** LFP (Lithium Iron Phosphate)
        * **Capacity:** 5 MW / 10 MWh
        * **Primary Role:** Peak Shaving during 9MW concert spikes & arbitrage.
        * **Local Impact:** Eliminates local transformer overload risks.
        """)
    else:
        st.markdown("""
        * **Load Profile Type:** Variable HVAC & Lighting
        * **Contribution to Peak:** High synchronous draw during events.
        * **Mitigation Strategy:** Managed via central BESS discharging schedule.
        """)
    
    # Mini metrics for the zone
    st.metric("Local Peak Reduction", "3.8 MW", delta="-42%")
    st.metric("Estimated Daily Savings", "1,041 EUR", delta="Bankable")
