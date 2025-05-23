import streamlit as st

st.set_page_config(
    page_title="Financial Dashboard",    # titolo della scheda del browser
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("👋 Benvenuto nella dashboard finanziaria")
st.write("Seleziona una categoria dal menu a sinistra per iniziare.")
