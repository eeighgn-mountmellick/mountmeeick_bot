import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta
import os

st.set_page_config(page_title="River Sentinel", layout="wide")
STATIONS = {"14121": "Manor Road", "14120": "Chapel Street"}

st.title("🌊 River Sentinel Dashboard")

for st_id, name in STATIONS.items():
    # Get the directory the script is in
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(curr_dir, f"history_{st_id}_0001.csv")
    # file = f"history_{st_id}_0001.csv"
    if os.path.exists(file_path):
        # 1. Load the data
        df = pd.read_csv(file_path)
        
        # 2. FORCE DATA TYPES (The Fix)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce') # Converts text to numbers
        df = df.dropna(subset=['value']) # Removes any empty or broken rows
        
        if len(df) > 0:
            latest = df.iloc[-1]
            # Calculate rate using the last 4 records (1 hour)
            rate = latest['value'] - df.iloc[-5]['value'] if len(df) > 4 else 0
            
            # Metrics
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric(f"{name} Level", f"{latest['value']:.3f}m", f"{round(rate*100,1)} cm/hr")
            
            # Forecast
            f_time = latest['datetime'] + timedelta(hours=2)
            f_val = latest['value'] + (rate * 2)

            # Plot
            fig = go.Figure()
            
            # Actual Data
            fig.add_trace(go.Scatter(
                x=df['datetime'], 
                y=df['value'], 
                name="Actual Level (m)", 
                line=dict(color='#00CC96', width=3)
            ))
            
            # Forecast Line
            fig.add_trace(go.Scatter(
                x=[latest['datetime'], f_time], 
                y=[latest['value'], f_val], 
                name="2hr Projection", 
                line=dict(dash='dash', color='#EF553B')
            ))

            # Styling the axes to ensure they show decimal values
            fig.update_layout(
                template="plotly_dark",
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                yaxis=dict(title="Meters (OD)", tickformat=".2f"),
                hovermode="x unified"
            )
            
            fig.add_hline(y=0.8, line_dash="dot", line_color="red", annotation_text="Flood Alert")
            st.plotly_chart(fig, use_container_width=True)
