from common.functions import *
from backend.salary.relatech import process_relatech_salary
import plotly.express as px
import pandas as pd
import streamlit as st

# --- CONFIG ---
MONGO_URI = MONGO_URI
MONGO_DATABASE = MONGO_DATABASE
COLLECTION_NAME = "salary"

# --- LETTURA DATI ---
df = read_mongo_collection(COLLECTION_NAME)
if df.empty:
    st.warning("Nessun dato disponibile.")
    st.stop()

# Preparazione DataFrame
df['data_busta_paga'] = pd.to_datetime(df['data_busta_paga'])
df['mese'] = df['data_busta_paga'].dt.strftime('%Y-%m')
df['anno'] = df['data_busta_paga'].dt.year

oggi = pd.Timestamp.today()

# Calcoli
netto_annuo = df['netto_busta_paga'].sum()
# Filtra i record con ore_ordinarie diverse da zero
df_validi = df[df['ore_ordinarie'] != 0]
media_netto = df['netto_busta_paga'].sum() / len(df_validi) if len(df_validi) > 0 else 0
tasse_totali = df['totale_trattenute'].sum()
perc_tasse_lordo = (df['totale_trattenute'] / df['totale_competenze_lorde']).fillna(0).mean() * 100
tfr_totale = df['quota_tfr_lorda'].sum()
costo_orario_lordo = (df['totale_competenze_lorde'] / df['ore_ordinarie'].replace(0, pd.NA)).mean()

# Calcolo netto ultimo mese e confronto
df_sorted = df.sort_values(by='data_busta_paga')
ultimo = df_sorted.iloc[-1]['netto_busta_paga'] if len(df_sorted) >= 1 else 0
precedente = df_sorted.iloc[-2]['netto_busta_paga'] if len(df_sorted) >= 2 else 0
diff_mensile = ultimo - precedente
perc_diff_mensile = (diff_mensile / precedente * 100) if precedente != 0 else 0

# Calcolo netto ultimo anno e confronto
anni_presenti = sorted(df['anno'].unique())
ul_anno = anni_presenti[-1] if len(anni_presenti) >= 1 else 0
mese_ultimo = df_sorted.iloc[-1]['mese'] if len(df_sorted) >= 1 else "N/A"
prev_anno = anni_presenti[-2] if len(anni_presenti) >= 2 else 0
netto_ul_anno = df[df['anno'] == ul_anno]['netto_busta_paga'].sum()
netto_prev_anno = df[df['anno'] == prev_anno]['netto_busta_paga'].sum()
diff_annuo = netto_ul_anno - netto_prev_anno
perc_diff_annuo = (diff_annuo / netto_prev_anno * 100) if netto_prev_anno != 0 else 0

# Layout Streamlit
st.title("\U0001F4CA Dashboard Buste Paga")

# Card metriche su 2 righe (4 + 4)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Netto Totale", f"€ {format_number_italian(netto_annuo)}")
col2.metric("Media Netto Mensile", f"€ {format_number_italian(media_netto)}")
col3.metric("Tasse Totali", f"€ {format_number_italian(tasse_totali)}")
col4.metric("% Tasse su Lordo", f"{format_number_italian(perc_tasse_lordo)}%")

col5, col6, col7, col8 = st.columns(4)
col5.metric("TFR Totale", f"€ {format_number_italian(tfr_totale)}")
col6.metric("Costo Orario Lordo Medio", f"€ {format_number_italian(costo_orario_lordo)}" if not pd.isna(costo_orario_lordo) else "n.d.")

# Netto Ultimo Mese con delta colorato
delta_color_mese = "normal" if diff_mensile >= 0 else "inverse"
col7.metric(
    f"Netto Ultimo Mese ({mese_ultimo})",
    f"€ {format_number_italian(ultimo)}",
    f"€ {format_number_italian(diff_mensile)} ({format_number_italian(perc_diff_mensile)}%)",
    delta_color=delta_color_mese
)

# Netto Ultimo Anno con delta colorato
delta_color_anno = "normal" if diff_annuo >= 0 else "inverse"
col8.metric(
    f"Netto Ultimo Anno ({ul_anno})",
    f"€ {format_number_italian(netto_ul_anno)}",
    f"€ {format_number_italian(diff_annuo)} ({format_number_italian(perc_diff_annuo)}%)",
    delta_color=delta_color_anno
)

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
df_filtrato = df[df['mese'] >= data_limite]

# Aggregazione per mese per evitare duplicati nei grafici
df_agg = df_filtrato.groupby('mese').agg({
    'netto_busta_paga': 'sum',
    'totale_trattenute': 'sum',
    'quota_tfr_lorda': 'sum'
}).reset_index()

# Grafico trend netto mensile con label (area chart)
fig_netto = px.area(df_agg, x='mese', y='netto_busta_paga', title='\U0001F4C8 Netto Mensile', markers=True, text='netto_busta_paga')
fig_netto.update_traces(
    text=df_agg['netto_busta_paga'].apply(lambda x: f"€ {format_compact(x)}"),
    textposition='top center',
    line_color='green',
    fillcolor='rgba(0,128,0,0.2)'
)
fig_netto.update_layout(xaxis_title=None, yaxis_title=None)
st.plotly_chart(fig_netto, use_container_width=True)

# Grafico composizione trattenute vs netto con label (aggiornato per testo compatto)
texts_trattenute = df_agg['totale_trattenute'].apply(format_compact)
texts_netto = df_agg['netto_busta_paga'].apply(format_compact)

fig_bar = px.bar(df_agg, x='mese', y=['totale_trattenute', 'netto_busta_paga'],
                 barmode='group', title='\U0001F4B8 Trattenute vs Netto')

fig_bar.data[0].text = texts_trattenute.apply(lambda x: f"€ {x}")
fig_bar.data[1].text = texts_netto.apply(lambda x: f"€ {x}")
fig_bar.update_traces(textposition='outside')
st.plotly_chart(fig_bar, use_container_width=True)

# Grafico TFR mensile con label
fig_tfr = px.bar(df_agg, x='mese', y='quota_tfr_lorda', title='\U0001F4E6 TFR Mensile Accantonato')
fig_tfr.update_traces(text=df_agg['quota_tfr_lorda'].apply(lambda x: f"€ {format_compact(x)}"), textposition='outside')
st.plotly_chart(fig_tfr, use_container_width=True)

# Tabella ferie e permessi
st.subheader("\U0001F4C5 Ferie e Permessi Residui")
st.dataframe(df[['mese', 'ferie_residue', 'permessi_residui']].sort_values(by='mese', ascending=False))

# --- NAVIGAZIONE ---
st.markdown("---")
colx1, colx2 = st.columns(2)

with colx1:
    clear_collection = st.checkbox("Ricalcola tutto", value=False)
    if st.button("⚙️ Ricalcola Dati"):
        with st.spinner("Avvio backend..."):
            try:
                process_relatech_salary(clear_collection)
                st.success("Backend completato.")
            except Exception as e:
                st.error(f"Errore durante il salvataggio o l'elaborazione: {e}")
