# carbon_dashboard_clean.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# ========================================
# Page Config
# ========================================
st.set_page_config(
    page_title="🌱 CarbonSense AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# CSS Styling (Clean, no neon)
# ========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700&display=swap');
* { font-family: 'Inter', sans-serif; scroll-behavior: smooth; }
body { background: radial-gradient(circle at 20% 80%, #0A7C5E 0%, #1E3A8A 50%, #000000 100%); }

.hero-section { background: linear-gradient(135deg, #00D4AA 0%, #0A7C5E 50%, #1E3A8A 100%);
    border-radius: 40px; padding: 4rem; margin: 2rem 0; text-align: center; }

.nano-card { background: rgba(255,255,255,0.03); backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; padding: 2rem; }

.chart-container { background: rgba(0,0,0,0.3); border-radius: 24px; padding: 2rem; margin: 1rem 0; backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); }

.ai-insight { background: linear-gradient(135deg, #FF6B6B, #FF8E8E); border-radius: 20px; padding: 1.5rem; margin: 1rem 0; color: white; font-weight: 600; }
.urgency-high { background: linear-gradient(135deg, #FF6B6B, #FF5252); }
.urgency-med  { background: linear-gradient(135deg, #FFD93D, #FFC107); }
.urgency-low  { background: linear-gradient(135deg, #00D4AA, #00BFA5); }

.sidebar-custom { background: linear-gradient(180deg, rgba(10,124,94,0.9) 0%, rgba(30,58,138,0.9) 100%);
    backdrop-filter: blur(20px); border-radius: 24px; border: 1px solid rgba(255,255,255,0.2); padding:1rem; }
</style>
""", unsafe_allow_html=True)

# Hero section
st.markdown("""
<div class="hero-section">
    <h1 style="font-weight:700; color:#00D4AA;">CARBONSENSE AI</h1>
    <p style="font-size:1.4rem; opacity:0.9; margin:2rem 0;">
    Real-Time Carbon Intelligence • Mission Control Dashboard
    </p>
</div>
""", unsafe_allow_html=True)

# ========================================
# Load CSV
# ========================================
uploaded_file = st.sidebar.file_uploader("🚀 Launch Dataset", type=['csv'])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if 'date' not in df.columns or 'co2_kg' not in df.columns:
        st.error("CSV must have 'date' and 'co2_kg' columns.")
        st.stop()

    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month_name()
    df['year_month'] = df['date'].dt.to_period('M').astype(str)

    # Sidebar filters
    st.sidebar.markdown('<div class="sidebar-custom">', unsafe_allow_html=True)
    st.sidebar.markdown("### 🎛️ Filters")
    if 'department' in df.columns:
        dept_filter = st.sidebar.multiselect("Department", df['department'].unique(), default=df['department'].unique())
        df = df[df['department'].isin(dept_filter)]
    if 'location' in df.columns:
        loc_filter = st.sidebar.multiselect("Location", df['location'].unique(), default=df['location'].unique())
        df = df[df['location'].isin(loc_filter)]
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Metrics
    total_emission = df['co2_kg'].sum()
    high_emission_events = (df['co2_kg'] > 100).sum()
    co2_per_hour = df['co2_kg'].mean()

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"""<div class="nano-card">
        <h3 style="color:#94A3B8;">TOTAL EMISSIONS</h3>
        <h1 style="color:#00D4AA;">{total_emission:,.0f} kg</h1>
    </div>""", unsafe_allow_html=True)

    col2.markdown(f"""<div class="nano-card">
        <h3 style="color:#F87171;">CRITICAL ALERTS</h3>
        <h1 style="color:#EF4444;">{high_emission_events}</h1>
    </div>""", unsafe_allow_html=True)

    col3.markdown(f"""<div class="nano-card">
        <h3 style="color:#94A3B8;">EFFICIENCY</h3>
        <h1 style="color:#00D4AA;">{co2_per_hour:.1f} kg/hr</h1>
    </div>""", unsafe_allow_html=True)

    # ========================================
    # Charts Section
    # ========================================
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)

    # Pie chart: Emissions by Department
    if 'department' in df.columns:
        dept_summary = df.groupby('department')['co2_kg'].sum().reset_index()
        fig_pie = px.pie(dept_summary, names='department', values='co2_kg', title="🏢 Emissions by Department",
                         color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Bar chart: Monthly Emissions
    monthly = df.groupby('year_month')['co2_kg'].sum().reset_index()
    fig_bar = px.bar(monthly, x='year_month', y='co2_kg', title="📊 Monthly Carbon Emissions",
                     text='co2_kg', color='co2_kg', color_continuous_scale='Viridis')
    fig_bar.update_layout(xaxis_title="Month", yaxis_title="CO₂ Emissions (kg)", showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    # 3D Temporal Emissions Chart
    fig_3d = px.scatter_3d(monthly, x='year_month', y='co2_kg', z=np.arange(len(monthly)),
                           color='co2_kg', title="📈 Temporal Emissions 3D")
    st.plotly_chart(fig_3d, use_container_width=True)

    # ========================================
    # Filtered Emissions
    # ========================================
    threshold = st.slider("Show emissions above (kg CO₂):", 0, int(df['co2_kg'].max()), 50)
    filtered_df = df[df['co2_kg'] > threshold]
    st.subheader(f"Filtered Emissions > {threshold} kg CO₂")

    # Table view
    st.dataframe(filtered_df)

    # Bar chart of filtered emissions
    fig_filtered = px.bar(filtered_df, x='date', y='co2_kg', color='co2_kg',
                          title=f"Filtered Emissions > {threshold} kg",
                          color_continuous_scale='Viridis')
    st.plotly_chart(fig_filtered, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ========================================
    # AI Insights
    # ========================================
    st.markdown("### 🤖 AI MISSION BRIEFING")
    if 'department' in df.columns:
        top_dept = df.groupby('department')['co2_kg'].sum().idxmax()
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"""<div class="ai-insight urgency-high"><h4>🚨 IMMEDIATE ACTION</h4>
        <p><strong>{top_dept}</strong> = {df[df['department']==top_dept]['co2_kg'].sum():.0f} kg</p></div>""", unsafe_allow_html=True)
        col2.markdown(f"""<div class="ai-insight urgency-med"><h4>⚠️ HIGH RISK</h4>
        <p>{high_emission_events} critical events detected</p></div>""", unsafe_allow_html=True)
        col3.markdown(f"""<div class="ai-insight urgency-low"><h4>✅ EFFICIENCY</h4>
        <p>{co2_per_hour:.1f} kg CO₂ per hour</p></div>""", unsafe_allow_html=True)

else:
    st.info("Upload a CSV with at least 'date' and 'co2_kg'. Optional: 'department' and 'location'.")