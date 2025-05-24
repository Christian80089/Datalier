from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import  streamlit as st
import json

# Dati di Mongo DB
MONGO_URI = st.secrets["MONGO_URI"]
MONGO_DATABASE = "Datalier"

# Dati del service account (estratti dal JSON)
GOOGLE_DRIVE_JSON_CREDENTIALS = json.loads(st.secrets["GOOGLE_DRIVE_CREDENTIALS_PATH"])

GOOGLE_DRIVE_SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_DRIVE_JSON_CREDENTIALS, GOOGLE_DRIVE_SCOPE)
drive_service = build("drive", "v3", credentials=creds)