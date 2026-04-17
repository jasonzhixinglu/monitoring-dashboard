import streamlit as st
from src.monitor_config import CHINA
from src.page_utils import render_country_page

st.set_page_config(page_title="China Monitor", layout="wide")
st.title("China Monitor")
render_country_page("China", CHINA)
