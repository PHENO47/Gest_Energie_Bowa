
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

def executer_regression(df):
    # Régression multiple : Expliquer la facture par la conso et le délestage
    X = df[['Consommation_kWh', 'Heures_Delestage']]
    y = df['Montant_Facture']
    model = LinearRegression().fit(X, y)
    return model, model.score(X, y)

def executer_pca(df):
    # On ne prend que les colonnes numériques pour la réduction de dimension
    colonnes_numeriques = df.select_dtypes(include=['number'])
    if colonnes_numeriques.shape[1] >= 2:
        pca = PCA(n_components=2)
        composantes = pca.fit_transform(colonnes_numeriques)
        return composantes, pca.explained_variance_ratio_
    return None, None

def executer_clustering(df):
    # Segmentation des consommateurs en 3 groupes
    X = df[['Consommation_kWh', 'Montant_Facture']]
    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X)
    return kmeans.labels_
