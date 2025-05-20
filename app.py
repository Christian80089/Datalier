from taipy import Gui
from pymongo import MongoClient
import pandas as pd

mongo_uri = "mongodb+srv://christian:Christian80089@clusterfree.0b1sfgw.mongodb.net/?retryWrites=true&w=majority&appName=ClusterFree"
database = "Datalier"

# Connessione a MongoDB
client = MongoClient(mongo_uri)
db = client[database]
collection = db["bank_transactions"]

# Lettura dati da MongoDB (tutti i documenti)
docs = list(collection.find())

# Converti i dati in DataFrame pandas per visualizzare facilmente
# Rimuovo l'_id perché spesso è un ObjectId non serializzabile in tabella
for d in docs:
    d.pop("_id", None)

df = pd.DataFrame(docs)

# Codice Taipy GUI
page = """
# Tabella dati da MongoDB

<|{df}|table|pagination|page_size=10|columns={list(df.columns)}|>
"""

# Crea GUI e avvia
Gui(page).run()
