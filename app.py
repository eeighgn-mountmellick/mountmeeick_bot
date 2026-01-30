import sys

# Workaround for the removed imghdr module in Python 3.13+
try:
    import imghdr
except ImportError:
    import types
    m = types.ModuleType("imghdr")
    m.what = lambda filename, h=None: None  # Simple dummy function
    sys.modules["imghdr"] = m

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta
import os

st.set_page_config(page_title="River Sentinel", layout="wide")
STATIONS = {"14121": "Manor Road", "14120": "Chapel Street"}

st.title("🌊 River Sentinel Dashboard")

for st_id, name in STATIONS.items():
    file = f"history_{st_id}_0001.csv"
    if os.path.exists(file):
        df = pd.read_csv(file)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce') # Converts text to numbers
        df = df.dropna(subset=['value']) # Removes any empty or broken rows
        latest = df.iloc[-1]
        rate = latest['value'] - df.iloc[-5]['value'] if len(df) > 4 else 0
        
        # Metrics
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric(f"{name} Level", f"{latest['value']}m", f"{round(rate*100,1)} cm/hr")
        
        # Forecast Math: L_{t+120} = L_t + (Rate * 2)
        f_time = latest['datetime'] + timedelta(hours=2)
        f_val = latest['value'] + (rate * 2)

        # Plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['datetime'], y=df['value'], name="Actual", line=dict(color='#00CC96')))
        fig.add_trace(go.Scatter(x=[latest['datetime'], f_time], y=[latest['value'], f_val], 
                                 name="2hr Forecast", line=dict(dash='dash', color='#EF553B')))
        fig.add_hline(y=0.8, line_dash="dot", line_color="red", annotation_text="Flood Threshold")
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
