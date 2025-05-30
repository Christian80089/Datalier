import gspread
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaIoBaseUpload
import io
import csv
import re
from pymongo import MongoClient
import pandas as pd
import hashlib
from datetime import datetime
from common.config import *
import time

def normalize_column_names(columns):
    # Trasforma in lowercase e sostituisce tutto ciò che non è lettera o numero con _
    normalized = []
    for col in columns:
        col = col.lower()
        col = re.sub(r'[^a-z0-9]+', '_', col)  # sostituisce sequenze non alfanumeriche con _
        col = col.strip('_')  # rimuove eventuali _ iniziali o finali
        normalized.append(col)
    return normalized

def read_sheet_from_folder(sheet_id):
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    file_name = spreadsheet.title
    sheet = spreadsheet.sheet1
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    # Normalizzo i nomi delle colonne
    df.columns = normalize_column_names(df.columns)

    df['source_file'] = file_name

    return df

def read_csv_from_folder(folder_id, google_drive_service):
    query = f"'{folder_id}' in parents and mimeType='text/csv'"
    results = google_drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        raise ValueError(f"No CSV files found in folder ID: {folder_id}")

    dataframes = []
    for file in files:
        file_id = file['id']
        file_name = file['name']

        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
        sample = fh.read(2048).decode('utf-8', errors='ignore')
        fh.seek(0)

        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample, delimiters=[',', ';'])
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ','

        df = pd.read_csv(fh, delimiter=delimiter)
        # print(file_name)

        # Normalizzo i nomi delle colonne
        df.columns = normalize_column_names(df.columns)

        df['source_file'] = file_name
        dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True)

def save_uploaded_csv_to_drive(uploaded_file, folder_id, google_drive_service):
    if uploaded_file is None:
        raise ValueError("Nessun file selezionato")

    # Leggi il contenuto del CSV in un DataFrame
    content = uploaded_file.read()
    sample = content[:2048].decode("utf-8", errors="ignore")

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";"])
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = ","

    # print(f"Delimiter rilevato: {delimiter!r}")
    df = pd.read_csv(io.BytesIO(content), delimiter=delimiter, on_bad_lines='skip')

    # Aggiungi timestamp al nome del file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = uploaded_file.name.rsplit(".", 1)[0]
    file_name = f"{original_name}_{timestamp}.csv"

    # Scrivi il contenuto del DataFrame in un oggetto BytesIO
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False, sep=delimiter)
    buffer.seek(0)

    media = MediaIoBaseUpload(buffer, mimetype='text/csv')

    # Carica su Google Drive
    file_metadata = {
        "name": file_name,
        "parents": [folder_id],
        "mimeType": "text/csv"
    }

    uploaded = google_drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name"
    ).execute()

    return {
        "file_id": uploaded["id"],
        "file_name": uploaded["name"],
        "dataframe": df
    }

def wait_for_file_on_drive(google_drive_service, folder_id, file_name, timeout=30, poll_interval=3):
    """
    Attende fino a `timeout` secondi che il file con `file_name`
    sia disponibile nella cartella Drive `folder_id`.
    Ritorna True se trovato, False se timeout.
    """
    query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
    elapsed = 0

    while elapsed < timeout:
        results = google_drive_service.files().list(
            q=query,
            spaces='drive',
            fields="files(id, name)",
            pageSize=1
        ).execute()

        files = results.get('files', [])
        if files:
            return True  # File trovato

        time.sleep(poll_interval)
        elapsed += poll_interval

    return False  # Timeout, file non trovato

def read_mongo_collection(collection_name: str, mongo_uri: str = MONGO_URI, database_name: str = MONGO_DATABASE):
    """
    Legge tutti i documenti da una collection MongoDB e li restituisce come lista di dizionari.

    :param mongo_uri: URI di connessione MongoDB
    :param database_name: nome del database
    :param collection_name: nome della collection
    :return: lista di documenti (dizionari)
    """
    client = MongoClient(mongo_uri)
    db = client[database_name]
    collection = db[collection_name]
    docs = list(collection.find())
    client.close()

    if not docs:
        print("La collection è vuota.")
        pandas_df = pd.DataFrame()
    else:
        for doc in docs:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])

        # Converti in pandas DataFrame
        pandas_df = pd.DataFrame(docs)

    return pandas_df


def write_pandas_df_to_mongo(
        pandas_df,
        collection_name: str,
        mongo_uri: str = MONGO_URI,
        database_name: str = MONGO_DATABASE
):
    """
    Scrive i dati di un pandas DataFrame su una collection MongoDB specificata.

    :param pandas_df: DataFrame pandas da salvare
    :param collection_name: nome della collection Mongo
    :param mongo_uri: URI MongoDB (default)
    :param database_name: nome database (default)
    """
    client = MongoClient(mongo_uri)
    db = client[database_name]
    collection = db[collection_name]

    docs = pandas_df.to_dict(orient='records')

    if docs:
        result = collection.insert_many(docs)
        print(f"{len(result.inserted_ids)} documenti inseriti in '{collection_name}'.")
    else:
        print("DataFrame vuoto, nessun documento da inserire.")

    client.close()


def clear_mongo_collection(
        collection_name: str,
        mongo_uri: str = MONGO_URI,
        database_name: str = MONGO_DATABASE
):
    client = MongoClient(mongo_uri)
    db = client[database_name]
    collection = db[collection_name]

    result = collection.delete_many({})
    print(f"Cancellati {result.deleted_count} documenti dalla collection '{collection_name}'.")

    client.close()

# Concatena i valori riga per riga e calcola sha256
def compute_sha256_column(df: pd.DataFrame, columns: list[str], output_col: str = "primary_key") -> pd.DataFrame:
    """
    Aggiunge una colonna con hash SHA-256 calcolata dalla concatenazione dei valori delle colonne specificate.

    Args:
        df (pd.DataFrame): Il DataFrame di input.
        columns (list[str]): Le colonne da concatenare per calcolare l'hash.
        output_col (str): Il nome della colonna di output contenente l'hash.

    Returns:
        pd.DataFrame: Una copia del DataFrame con la colonna hash aggiunta.
    """
    df_copy = df.copy()

    df_copy[output_col] = df_copy[columns].astype(str).agg("|".join, axis=1).apply(
        lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest()
    )

    return df_copy

def add_script_datetime_column(
    df: pd.DataFrame,
    timestamp_col: str = "script_datetime"
) -> pd.DataFrame:
    """
    Aggiunge una colonna con la data e ora correnti per ogni record.

    Args:
        df (pd.DataFrame): Il DataFrame di input.
        timestamp_col (str): Il nome della colonna da aggiungere con il timestamp.

    Returns:
        pd.DataFrame: Una copia del DataFrame con la colonna timestamp aggiunta.
    """
    df_copy = df.copy()
    current_timestamp = datetime.now()

    df_copy[timestamp_col] = current_timestamp

    return df_copy

# --- Funzione per formato compatto con lettere (k, M, B) ---
def format_compact(num):
    abs_num = abs(num)
    if abs_num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif abs_num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif abs_num >= 1_000:
        return f"{num/1_000:.1f}k"
    else:
        return str(num)

def format_number_italian(num, decimals=2):
    # Formatta con 2 decimali con il separatore inglese (virgola per migliaia e punto per decimali)
    s = f"{num:,.{decimals}f}"
    # Sostituisci virgola (separatore migliaia) con temporaneo '#'
    s = s.replace(",", "#")
    # Sostituisci punto (decimali) con virgola
    s = s.replace(".", ",")
    # Sostituisci temporaneo '#' con punto (separatore migliaia italiano)
    s = s.replace("#", ".")
    return s
