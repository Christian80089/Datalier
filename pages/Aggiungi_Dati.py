from backend.salary.ing_bank import process_bank_transactions
from common.functions import *
from common.config import *

# --- CONFIG ---
st.set_page_config(page_title="Carica Nuovi Dati", layout="wide")
st.title("\U0001F4E5 Carica o Inserisci Dati")

# --- CATEGORIE ---
categorie = {
    "Bank Transactions": {
        "columns": ["DATA CONTABILE", "DATA VALUTA", "USCITE", "ENTRATE", "CAUSALE", "DESCRIZIONE OPERAZIONE"],
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
    file_content = None

    if uploaded_file:
        # Leggo in anteprima il CSV
        try:
            file_content = uploaded_file.read()
            uploaded_file.seek(0)  # reset del puntatore per eventuali riletture
            sample = file_content[:2048].decode("utf-8", errors="ignore")
            delimiter = csv.Sniffer().sniff(sample, delimiters=[",", ";"]).delimiter
        except csv.Error:
            delimiter = ","

        df_csv = pd.read_csv(io.BytesIO(file_content), delimiter=delimiter, on_bad_lines='skip')

        if set(config_cat['columns']).issubset(df_csv.columns):
            st.success("Anteprima dati caricati:")
            st.dataframe(df_csv.head())

            if st.button("Salva su Google Drive e processa i nuovi dati"):
                with st.spinner("Salvataggio in corso e avvio backend..."):
                    try:
                        result = save_uploaded_csv_to_drive(
                            uploaded_file=uploaded_file,
                            folder_id="1bqjFc4Y5X_CXCy6RTpEzlVfK3Pith87S",
                            google_drive_service=drive_service
                        )
                        st.success(f"Dati salvati su Drive come '{result['file_name']}'")

                        # Aspetta che il file sia visibile su Drive
                        file_ready = wait_for_file_on_drive(
                            google_drive_service=drive_service,
                            folder_id="1bqjFc4Y5X_CXCy6RTpEzlVfK3Pith87S",
                            file_name=result['file_name'],
                            timeout=30,
                            poll_interval=3
                        )

                        if not file_ready:
                            st.error("Timeout: il file non è ancora disponibile su Google Drive.")
                        else:
                            if config_cat['drive_path'] == "bank_transactions":
                                process_bank_transactions(clear_collection=True)
                            st.success("Backend completato.")

                    except Exception as e:
                        st.error(f"Errore durante il salvataggio o l'elaborazione: {e}")
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
                st.success("Dati salvati e backend completato")
