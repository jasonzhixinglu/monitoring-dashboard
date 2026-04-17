import streamlit as st
from src.monitor_config import JAPAN
from src.page_utils import render_country_page

st.set_page_config(page_title="Japan Monitor", layout="wide")
st.title("Japan Monitor")
render_country_page("Japan", JAPAN)
