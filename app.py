import streamlit as st
from src.data_access import check_files, load_data, load_metadata

st.set_page_config(page_title="Monitoring Dashboard", layout="wide")

st.title("Monitoring Dashboard")
st.write("Select a country from the sidebar.")

st.divider()
st.subheader("Data source status")

status = check_files()
haver_path = status["haver_data_path"]
data_ok = status["data_parquet"]
meta_ok = status["metadata_parquet"]

st.write(f"**haver-data path:** `{haver_path}`")
st.write(f"**data.parquet:** {'✅ found' if data_ok else '❌ not found'}")
st.write(f"**metadata.parquet:** {'✅ found' if meta_ok else '❌ not found'}")

if data_ok and meta_ok:
    st.success("Both files found. Showing previews.")
    col1, col2 = st.columns(2)
    with col1:
        st.caption("data.parquet — first 5 rows")
        st.dataframe(load_data().head())
    with col2:
        st.caption("metadata.parquet — first 5 rows")
        st.dataframe(load_metadata().head())
else:
    st.warning(
        "One or more parquet files are missing. "
        "Point the app to your local haver-data repo by setting:\n\n"
        "```\nexport HAVER_DATA_REPO=/workspaces/haver-data\n```\n\n"
        "Then restart the Streamlit server."
    )
