"""Streamlit interface for the reconstructed deterministic planner."""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.demo_data import load_demo_pois
from src.planner import build_itinerary, confirm_itinerary


st.set_page_config(page_title="Tokyo Trip Orchestrator", layout="wide")
st.title("Tokyo Trip Orchestrator")
st.caption("Reconstructed portfolio prototype. Planning is deterministic; sample POIs are demo data.")

pois = load_demo_pois()
selected_names = st.multiselect("Saved places", [poi.name for poi in pois], default=[poi.name for poi in pois])
start = st.date_input("Trip starts", value=date(2026, 9, 18))
days = st.slider("Trip length", 2, 7, 4)
pace = st.selectbox("Pace", ["relaxed", "moderate", "busy"], index=1)

if st.button("Build itinerary", type="primary"):
    selected = [poi for poi in pois if poi.name in selected_names]
    trip_days = [start + timedelta(days=index) for index in range(days)]
    itinerary = build_itinerary(selected, trip_days, pace)
    st.session_state["itinerary"] = itinerary

itinerary = st.session_state.get("itinerary")
if itinerary:
    st.metric("Checks flagged", itinerary.checks_flagged)
    for day in itinerary.days:
        st.subheader(day.day.strftime("%A, %d %B"))
        st.dataframe(pd.DataFrame([
            {"arrival": visit.arrival.strftime("%H:%M"), "place": visit.poi.name,
             "area": visit.poi.area, "duration_min": visit.poi.duration_minutes,
             "fixed": visit.locked}
            for visit in day.visits
        ]), hide_index=True, use_container_width=True)
        for warning in day.warnings:
            st.warning(warning)
    if st.button("Confirm itinerary"):
        if confirm_itinerary(itinerary):
            st.success("Itinerary confirmed.")
        else:
            st.error("Resolve the explained conflicts before confirmation.")
