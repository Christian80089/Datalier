import streamlit as st
import pandas as pd
from datetime import datetime
import subprocess

# --- CONFIG ---
st.set_page_config(page_title="Carica Nuovi Dati", layout="wide")
st.title("\U0001F4E5 Carica o Inserisci Dati")

# --- CATEGORIE ---
categorie = {
    "Bank Transactions": {
        "columns": ["data_valuta", "descrizione_operazione", "causale", "entrate", "uscite"],
        "drive_path": "bank_transactions"
    },
    # Aggiungi qui altre categorie
}

# --- SELEZIONE CATEGORIA ---
cat_selezionata = st.selectbox("Seleziona la categoria di dati", list(categorie.keys()))
config_cat = categorie[cat_selezionata]

# --- SCELTA MODALITÀ ---
modo = st.radio("Come vuoi aggiungere i dati?", ["Carica CSV", "Inserisci manualmente"])

# --- VARIABILI GLOBALI ---
data_oggi = datetime.today().strftime("%Y-%m")
nome_file = f"{config_cat['drive_path']}_{data_oggi}.csv"

# --- CARICAMENTO CSV ---
if modo == "Carica CSV":
    uploaded_file = st.file_uploader("Carica un file CSV", type=["csv"])
    if uploaded_file:
        df_csv = pd.read_csv(uploaded_file)
        if set(config_cat['columns']).issubset(df_csv.columns):
            st.success("Anteprima dati caricati:")
            st.dataframe(df_csv.head())
            if st.button("Salva su Google Drive ed Esegui Elabora Dati"):
                with st.spinner("Salvataggio in corso e avvio backend..."):
                    # save_to_drive_append_or_create(df_csv, nome_file, config_cat['drive_path'])
                    subprocess.run(["python", "backend_main.py"])
                    st.success("Dati salvati e backend completato")
        else:
            st.error("Il file CSV non contiene le colonne richieste.")

# --- INSERIMENTO MANUALE ---
else:
    st.markdown("### Inserisci i dati manualmente")
    if "righe_manuali" not in st.session_state:
        st.session_state.righe_manuali = []

    with st.form(key="form_riga"):
        nuova_riga = {}
        for col in config_cat['columns']:
            if "data" in col:
                nuova_riga[col] = st.date_input(col)
            elif "entrate" in col or "uscite" in col:
                nuova_riga[col] = st.number_input(col, value=0.0, step=0.01, format="%.2f")
            else:
                nuova_riga[col] = st.text_input(col)
        submitted = st.form_submit_button("Aggiungi Riga")

        if submitted:
            nuova_riga["data_valuta"] = pd.to_datetime(nuova_riga["data_valuta"]).strftime("%Y-%m-%d")
            st.session_state.righe_manuali.append(nuova_riga)
            st.success("Riga aggiunta correttamente.")

    if st.session_state.righe_manuali:
        df_manual = pd.DataFrame(st.session_state.righe_manuali)
        st.markdown("### Righe Inserite")
        st.dataframe(df_manual)

        if st.button("Salva tutte le righe ed Esegui Backend"):
            with st.spinner("Salvataggio in corso e avvio backend..."):
                # save_to_drive_append_or_create(df_manual, nome_file, config_cat['drive_path'])
                subprocess.run(["python", "backend_main.py"])
                st.success("Dati salvati e backend completato")
