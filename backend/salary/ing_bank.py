from common.config import *
from common.functions import *
from datetime import datetime

def process_bank_transactions(clear_collection: bool = False):
    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] ▶️ Inizio processo ETL")

    try:
        # === Estrazione ===
        FOLDER_ID = "1bqjFc4Y5X_CXCy6RTpEzlVfK3Pith87S"
        input_df = read_csv_from_folder(FOLDER_ID, drive_service)
        mongo_df = read_mongo_collection("bank_transactions")

        # === Trasformazione ===
        transform_df = input_df[input_df["causale"].notna()].copy()

        transform_df["data_contabile"] = pd.to_datetime(transform_df["data_contabile"], format="%d/%m/%Y", errors='coerce')
        transform_df["data_valuta"] = pd.to_datetime(transform_df["data_valuta"], format="%d/%m/%Y", errors='coerce')

        transform_df["uscite"] = (
            transform_df["uscite"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
            .fillna(0)
        )

        transform_df["entrate"] = (
            transform_df["entrate"]
            .astype(str)
            .str.replace("+", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
            .fillna(0)
        )

        cols_to_concat = [col for col in transform_df.columns if col != "primary_key"]
        transform_df = compute_sha256_column(transform_df, columns=cols_to_concat, output_col="primary_key")
        transform_df = add_script_datetime_column(transform_df, timestamp_col="script_date_time")

        # === Caricamento ===
        if clear_collection:
            clear_mongo_collection("bank_transactions")

        write_pandas_df_to_mongo(transform_df, "bank_transactions")

        end_time = datetime.now()
        duration = end_time - start_time

        print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Processo ETL completato.")
        print(f"⏱️ Durata totale: {duration}")
    except Exception as e:
        end_time = datetime.now()
        print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Errore nel processo ETL: {e}")