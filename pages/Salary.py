import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Salary")

st.title("💼 Metriche - Salary")

# MOCK: DataFrame di esempio (sarà sostituito da lettura MongoDB)
data = {
    "date": pd.date_range(start="2024-01-01", periods=6, freq='M'),
    "gross_salary": [3000, 3050, 3100, 3200, 3150, 3300],
    "net_salary": [2400, 2450, 2500, 2550, 2500, 2600]
}
df = pd.DataFrame(data)

# Visualizzazione tabellare
st.subheader("Dati Salario (mock)")
st.dataframe(df)

# Grafico
fig = px.line(df, x="date", y=["gross_salary", "net_salary"], markers=True, title="Evoluzione Salario")
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
