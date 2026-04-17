
import pandas as pd
import os

FILE_PATH = "data_energie_bowa.csv"

def initialiser_csv():
    if not os.path.exists(FILE_PATH):
        # On définit les colonnes dès le départ pour la robustesse
        df = pd.DataFrame(columns=['Quartier', 'Consommation_kWh', 'Heures_Delestage', 'Montant_Facture', 'Type_Abonnement'])
        df.to_csv(FILE_PATH, index=False)

def sauvegarder_donnee(data):
    df = pd.read_csv(FILE_PATH)
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(FILE_PATH, index=False)

def charger_donnees():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    return pd.DataFrame()
