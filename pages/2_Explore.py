import streamlit as st
from utils.io import load_weather
from charts.charts import chart_dashboard, chart_new_interactive_temp_minmax

st.set_page_config(page_title="Explore", layout="wide")
df = load_weather()

st.title("Interactive Exploratory View")
st.write("Use interaction to validate and extend the story—focus on one weather type, then zoom into a time window.")

st.altair_chart(chart_dashboard(df), use_container_width=True)

st.subheader("New interactive view: min/max temperature explorer")
st.write("Use the dropdown to filter weather type, then drag on the scatterplot to brush a region and inspect the temperature-range distribution.")
st.altair_chart(chart_new_interactive_temp_minmax(df), use_container_width=True)

st.markdown("**Guided prompts:**")
st.write("- Filter to one weather type (e.g., `sun`, `rain`)—does the temperature distribution shift?")
st.write("- Brush a specific year—do extremes cluster in particular periods?")
st.write("- Compare histogram shape across weather types—what changes most: center, spread, or tails?")
