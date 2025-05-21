from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

# Dati di Mongo DB
MONGO_URI = "mongodb+srv://christian:Christian80089@clusterfree.0b1sfgw.mongodb.net/?retryWrites=true&w=majority&appName=ClusterFree"
MONGO_DATABASE = "Datalier"

# Dati del service account (estratti dal JSON)
GOOGLE_DRIVE_JSON_CREDENTIALS = {
  "type": "service_account",
  "project_id": "databricks-project-460019",
  "private_key_id": "f1082fa747c99c8c52be1de5a81109a8d87c4e79",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQDPG0j5uKZNHMMp\noT9DboFxwOvATjeX6nm9Om4K0uGrk0xczMAgJGgVRljp1KoMYsrqpKc396FCMKqt\neMeEmNnFC0bmsnb5Uv/rOqMgmoll21E7GEOFovaNYjM4+mEVX1TyIuQ+dxCpzZri\nal4nMV45zNpBw7U8Fy5rSiaEzVVFziAd6w1O7WSU7pNjQ+i51+aXbHFT5b33u3kM\nTLbhPManRD64wabJ5hlaskHHdw+9JxGHJoW4PVjYJx60ZYs9hstXly/iJZw69gd1\nOgQ5DhBaQ/Nh4ZFT34o4iI0FWo0L5Y1Z9SO/vHLMcOZRMpmSjE12d51+AjHdTcYx\nXjhyvpgbAgMBAAECgf8F2SIXjpeMc/Zb9c77nRn4IoO6JQko/Sv9qmHHd0KRur8s\ngA2+imqRLCRsMhCChrascUDC7gnRCRmRMjqbQBI5cdpjgTR7O6U/JDdkgvJz4YYG\n/RFHktcZcPmMGqGgF7ebdSMVfosSlsgMuHKpPLV4x1lWEwiV5GgLifPQWhSokKEX\nO9lWH0SeBqrreh6bDvm5pZmryEcGsBjGhyuyvPJtvwaAjzwjeheod8rpo31bUcq6\n3c3BZpB8XlZB2vZjW5XZ0AI+HzBIkY2kUDP3Wi0EhGCEnaxG5v3PfCY8oisK1LbY\n0U6pUrYAycGsYmTVOD2f+YI+naf8W1+KhJiy8MECgYEA9oGLax7ouRm2YtuDUde6\n4pXawSjLSRNNM1uE4hHqle7T7mhdBlC87zUgh4vbm6oyUGWg0d4hBsRngIfl5epT\niSKf2wofpmdNbY6EfeLmhmzhrv9kcjaeNLv7ZN0BLxXGy+jtgqElneNJh7gwoNya\nyD+iXWzvC5wTAAORR2cE9vUCgYEA1xVG41QHKFXs0Zf2PA9vQrTqbd7VdGwPCi/8\n78kqRoxDpWKBkEjphIM39AIYTI8ME9wg4hhrckISRJm+Q/UWVNjLqe3aGdIEkZip\nGXOO4YV7+HlaMrHX1CMlnmH1sR+KXRAdeYrTdU6FNzcBS+XC94SKHdl2PHg7Scpm\nyjduSM8CgYBp4pV3iwxeTiwo5K/Q3QDayZHwvMwtdIwJznsS/K0ugCsq0kt7Jf0y\nJzj04F+RyxbXr//XhjnbhUwMStO24ePGGUhfN0cHHIKG19wTkv6AqY57tBp6cPme\nH01KMyCKECmXd1NmdEALRRFVqgnBX2FhOOxOgzdfXkhPDjk+WYMpbQKBgQCX6fZM\nwF/h1HbVPyDzIO+zzPa7raVUerJQvr5HWu2aMJ3i5WWf1G/jYY8WsJgbEvoz2Mn9\nB8R0Skh+3ZxugWBJg2quVkoy7Iy/jXT6fg1QKqj6QjQ8FDLeKgj7CjOv7BgdTTGU\nVEKw20nqStaGlf0UODAZjywc38r4fpYFhAtILwKBgFooiH24Za+cE/LnLP8p6054\nJwB+eGr53MYsNh+TkvS2LGvHlrWaI+iWYoc58KFIQgJiuXHmq1Dbh/C6GG6tUcKc\nzfuAtr5yAITSwYE+o8ztfKra0b3md2g2XApPPbBndI/QDL5SsAubw9lyT6IcDbfh\nxToLpw0Dgwl/0uS6xNr2\n-----END PRIVATE KEY-----\n",
  "client_email": "databricks-service-account@databricks-project-460019.iam.gserviceaccount.com",
  "client_id": "103619999303300614633",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/databricks-service-account%40databricks-project-460019.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

GOOGLE_DRIVE_SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_DRIVE_JSON_CREDENTIALS, GOOGLE_DRIVE_SCOPE)
drive_service = build("drive", "v3", credentials=creds)