import plotly.express as px
from common.functions import *

# --- CONFIG ---
MONGO_URI = MONGO_URI
MONGO_DATABASE = MONGO_DATABASE
COLLECTION_NAME = "bank_transactions"

# --- PAGE CONFIG ---
st.set_page_config(page_title="Bank Transactions", layout="wide")
st.title("\U0001F3E6 Metriche - Bank Transactions")

# --- LETTURA DATI ---
df = read_mongo_collection(COLLECTION_NAME)
if df.empty:
    st.warning("Nessun dato disponibile.")
    st.stop()

# --- PREPARAZIONE DATI ---
df['data_valuta'] = pd.to_datetime(df['data_valuta'])
df['mese'] = df['data_valuta'].dt.to_period("M").astype(str)
df['saldo'] = df['entrate'] + df['uscite']

# METRICHE GLOBALI
saldo_corrente = df['saldo'].sum()
tot_entrate = df['entrate'].sum()
tot_uscite = df['uscite'].sum()

# METRICHE MESE SCORSO vs PRECEDENTE
oggi = pd.Timestamp.today()
mese_corrente = oggi.to_period("M")
mese_scorso = (mese_corrente - 1).strftime("%Y-%m")
mese_prec = (mese_corrente - 2).strftime("%Y-%m")

df_mese_scorso = df[df['mese'] == mese_scorso]
df_mese_prec = df[df['mese'] == mese_prec]

saldo_scorso = df_mese_scorso['saldo'].sum()
saldo_prec = df_mese_prec['saldo'].sum()
saldo_delta = saldo_scorso - saldo_prec
saldo_perc = (saldo_delta / abs(saldo_prec)) * 100 if saldo_prec != 0 else 0

entrate_scorso = df_mese_scorso['entrate'].sum()
entrate_prec = df_mese_prec['entrate'].sum()
entrate_delta = entrate_scorso - entrate_prec
entrate_perc = (entrate_delta / abs(entrate_prec)) * 100 if entrate_prec != 0 else 0

uscite_scorso = df_mese_scorso['uscite'].sum()
uscite_prec = df_mese_prec['uscite'].sum()
uscite_delta = uscite_scorso - uscite_prec
uscite_perc = (uscite_delta / abs(uscite_prec)) * 100 if uscite_prec != 0 else 0

# --- INPUT RISPARMI ---
with st.expander("💰 Inserisci Risparmi", expanded=False):
    col_risparmi = st.columns(1)[0]
    risparmi = col_risparmi.number_input(
        "Inserisci l'importo dei tuoi risparmi (€):",
        min_value=0.0,
        step=100.0,
        format="%.2f"
    )
totale_disponibile = saldo_corrente + risparmi

# --- METRICHE ---
st.subheader("Panoramica Attuale")
col1, col2, col3, col4, col4_1 = st.columns(5)
col1.metric("Saldo Conto Corrente", format_number_italian(saldo_corrente) + " €")
col2.metric("Totale Entrate", format_number_italian(tot_entrate) + " €")
col3.metric("Totale Uscite", format_number_italian(tot_uscite) + " €")
col4.metric("Risparmi", format_number_italian(risparmi) + " €")
col4_1.metric("Saldo + Risparmi", format_number_italian(totale_disponibile) + " €")

st.subheader("Panoramica Mese Scorso")
col5, col6, col7 = st.columns(3)
col5.metric("Saldo Conto Corrente", format_number_italian(saldo_scorso) + " €", f"{saldo_perc:+.1f}% ({format_number_italian(saldo_delta)} €)")
col6.metric("Totale Entrate", format_number_italian(entrate_scorso) + " €", f"{entrate_perc:+.1f}% ({format_number_italian(entrate_delta)} €)")
col7.metric("Totale Uscite", format_number_italian(uscite_scorso) + " €", f"{uscite_perc:+.1f}% ({format_number_italian(uscite_delta)} €)")

# --- FILTRO TREND CON EXPANDER ---
st.subheader("Trend Mensili")
with st.expander("Filtro temporale (clicca per modificare)", expanded=False):
    mesi_opzioni = {
        "Ultimi 3 mesi": 3,
        "Ultimi 6 mesi": 6,
        "Ultimi 9 mesi": 9,
        "Ultimi 12 mesi": 12,
        "Ultimi 24 mesi": 24
    }
    scelta_mesi = st.selectbox(
        "Seleziona intervallo tempo",
        options=list(mesi_opzioni.keys()),
        index=list(mesi_opzioni.keys()).index("Ultimi 12 mesi")
    )
mesi_da_filtrare = mesi_opzioni[scelta_mesi]
data_limite = (oggi - pd.DateOffset(months=mesi_da_filtrare)).to_period("M").strftime("%Y-%m")

# --- DATI FILTRATI PER TREND ---
entrate_stipendio = df[df['causale'].str.contains("stipendio|pensione", case=False, na=False)]
entrate_trend = entrate_stipendio.groupby('mese')['entrate'].sum().reset_index()
uscite_trend = df.groupby('mese')['uscite'].sum().reset_index()
mutuo_trend = df[df['descrizione_operazione'].str.contains("mutuo 70500509750", case=False, na=False)].groupby('mese')['uscite'].sum().reset_index()
prestito_trend = df[df['descrizione_operazione'].str.contains("prestito 10101482304", case=False, na=False)].groupby('mese')['uscite'].sum().reset_index()

entrate_trend = entrate_trend[entrate_trend['mese'] >= data_limite]
uscite_trend = uscite_trend[uscite_trend['mese'] >= data_limite]
mutuo_trend = mutuo_trend[mutuo_trend['mese'] >= data_limite]
prestito_trend = prestito_trend[prestito_trend['mese'] >= data_limite]

entrate_trend["text"] = entrate_trend["entrate"].apply(format_compact)
uscite_trend["text"] = uscite_trend["uscite"].apply(format_compact)
mutuo_trend["text"] = mutuo_trend["uscite"].apply(format_compact)
prestito_trend["text"] = prestito_trend["uscite"].apply(format_compact)

# --- TREND CHARTS ---
col8, col9 = st.columns(2)

fig1 = px.area(
    entrate_trend,
    x='mese',
    y='entrate',
    title="Entrate: Stipendio",
    markers=True,
    text='text'
)
fig1.update_traces(textposition='top center', line_color='green', fillcolor='rgba(0,128,0,0.2)')
fig1.update_layout(xaxis_title=None, yaxis_title=None)
col8.plotly_chart(fig1, use_container_width=True)

fig2 = px.area(
    uscite_trend,
    x='mese',
    y='uscite',
    title="Tutte le Uscite",
    markers=True,
    text='text'
)
fig2.update_traces(textposition='top center', line_color='red', fillcolor='rgba(255,0,0,0.2)')
fig2.update_layout(xaxis_title=None, yaxis_title=None)
col9.plotly_chart(fig2, use_container_width=True)

col10, col11 = st.columns(2)

fig3 = px.area(
    mutuo_trend,
    x='mese',
    y='uscite',
    title="Uscite: MUTUO ARANCIO",
    markers=True,
    text='text'
)
fig3.update_traces(textposition='top center', line_color='orange', fillcolor='rgba(255,165,0,0.2)')
fig3.update_layout(xaxis_title=None, yaxis_title=None)
col10.plotly_chart(fig3, use_container_width=True)

fig4 = px.area(
    prestito_trend,
    x='mese',
    y='uscite',
    title="Uscite: PRESTITO ARANCIO",
    markers=True,
    text='text'
)
fig4.update_traces(textposition='top center', line_color='purple', fillcolor='rgba(128,0,128,0.2)')
fig4.update_layout(xaxis_title=None, yaxis_title=None)
col11.plotly_chart(fig4, use_container_width=True)

# --- NAVIGAZIONE ---
st.markdown("---")
colx1, colx2 = st.columns(2)

with colx1:
    if st.button("➕ Aggiungi nuovi dati"):
        st.switch_page("pages/Aggiungi_Dati.py")