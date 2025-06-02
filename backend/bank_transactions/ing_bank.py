from common.functions import *
from datetime import datetime

def process_ing_bank_transactions(clear_collection: bool = False):
    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] ▶️ Inizio processo ETL")

    try:
        # === Estrazione ===
        folder_id = "1bqjFc4Y5X_CXCy6RTpEzlVfK3Pith87S"
        mongo_collection_name = "bank_transactions"
        input_df = read_csv_from_folder(folder_id, drive_service)
        mongo_df = read_mongo_collection(mongo_collection_name)

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

        transform_df = transform_df[[
            "data_contabile",
            "data_valuta",
            "uscite",
            "entrate",
            "causale",
            "descrizione_operazione",
            "source_file"
        ]]

        cols_to_concat = [col for col in transform_df.columns if col != "primary_key"]
        transform_df = compute_sha256_column(transform_df, columns=cols_to_concat, output_col="primary_key")

        existing_keys = set(mongo_df["primary_key"])
        transform_df = transform_df[~transform_df["primary_key"].isin(existing_keys)]
        print(f"📊 Nuovi record da inserire: {len(transform_df)}")

        transform_df = add_script_datetime_column(transform_df, timestamp_col="script_date_time")

        # === Caricamento ===
        if clear_collection:
            clear_mongo_collection(mongo_collection_name)

        write_pandas_df_to_mongo(transform_df, mongo_collection_name)

        end_time = datetime.now()
        duration = end_time - start_time

        print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Processo ETL completato.")
        print(f"⏱️ Durata totale: {duration}")
    except Exception as e:
        end_time = datetime.now()
        print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Errore nel processo ETL: {e}")

if __name__ == "__main__":
    # Esegui con Python direttamente, utile per test locali
    process_ing_bank_transactions(clear_collection=True)