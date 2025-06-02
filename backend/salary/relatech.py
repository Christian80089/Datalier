from common.functions import *
from datetime import datetime

def process_relatech_salary(clear_collection: bool = False):
    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] ▶️ Inizio processo ETL")

    try:
        # === Estrazione ===
        sheet_id_salary = "14eRRxjjP8ifW98fh88rJ0m3mjum-itxi0RxRwBInjFw"
        mongo_collection_name = "salary"
        input_df = read_sheet_from_folder(sheet_id_salary)
        mongo_df = read_mongo_collection(mongo_collection_name)

        # === Trasformazione ===
        transform_df = input_df.copy()

        transform_df["data_busta_paga"] = pd.to_datetime(transform_df["data_busta_paga"], format="%d/%m/%Y", errors='coerce')

        transform_df = transform_df[[
            "data_busta_paga",
            "livello_contratto",
            "retribuzione_base_lorda",
            "totale_competenze_lorde",
            "irpef_lorda",
            "totale_trattenute",
            "netto_busta_paga",
            "quota_tfr_lorda",
            "ferie_residue",
            "permessi_residui",
            "ore_ordinarie",
            "ore_straordinario",
            "straordinario_pagato_lordo",
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
    process_relatech_salary(clear_collection=False)