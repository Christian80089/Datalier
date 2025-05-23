import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Insurance")

st.title("🛡️ Metriche - Insurance")

# MOCK: DataFrame di esempio (sarà sostituito da lettura MongoDB)
data = {
    "provider": ["Axa", "Allianz", "Generali", "Unipol"],
    "policy_type": ["Auto", "Casa", "Vita", "Salute"],
    "annual_cost": [450, 380, 600, 520],
    "expiration_date": pd.date_range(start="2025-06-30", periods=4, freq="Y")
}
df = pd.DataFrame(data)

# Visualizzazione tabellare
st.subheader("Polizze Assicurative (mock)")
st.dataframe(df)

# Grafico
fig = px.bar(df, x="provider", y="annual_cost", color="policy_type", title="Costo annuale per compagnia")
st.plotly_chart(fig, use_container_width=True)

# Pulsanti
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("🔙 Torna alle categorie"):
        st.switch_page("../Home.py")

with col2:
    if st.button("➕ Aggiungi nuovi dati"):
        st.info("Funzionalità da implementare.")
