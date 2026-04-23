# -*- coding: utf-8 -*-
import streamlit as st
import gestion_data as gd
import modeles as md
import plotly.express as px
from datetime import datetime

# 1. Configuration de la page (Design global)
st.set_page_config(
    page_title="Gest_Energie_Bowa", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé pour améliorer le design
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_stdio=True)

gd.initialiser_csv()
df = gd.charger_donnees()

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/lightning-bolt.png", width=80)
    st.title("Navigation")
    menu = st.radio(
        "Aller vers :",
        ["🏠 Accueil & Collecte", "📊 Analyses IA (EC2)", "📂 Historique & Export"]
    )
    st.markdown("---")
    st.info(f"📅 Date : {datetime.now().strftime('%d/%m/%Y')}")

# --- CONTENU PRINCIPAL ---
st.title("⚡ Gest_Energie_Bowa")
st.subheader("Système Intelligent de Suivi et d'Analyse Énergétique")

# 2. SECTION OBJECTIF (La pépite pour le prof)
with st.expander("ℹ️ À PROPOS DU PROJET (OBJECTIFS)", expanded=True):
    col_obj1, col_obj2 = st.columns([2, 1])
    with col_obj1:
        st.write("""
        **Contexte :** Dans un environnement marqué par des défis énergétiques, cette application 
        permet de centraliser les données de consommation et d'analyser l'impact des délestages.
        
        **Objectifs Techniques :**
        - **Collecte structurée** des données ménagères et professionnelles.
        - **Analyse prédictive** du montant des factures (Régression).
        - **Segmentation des profils** de consommation (Clustering K-Means).
        - **Réduction de dimension** pour la visualisation (PCA).
        """)
    with col_obj2:
        st.success("🎯 **Unité : INF232 (EC2)**\n\nProjet réalisé pour le suivi de la transition énergétique.")

st.markdown("---")

# --- LOGIQUE DU MENU ---

if menu == "🏠 Accueil & Collecte":
    # KPIs en haut
    if not df.empty:
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Collecte Totale", f"{len(df)} foyers")
        kpi2.metric("Conso Moyenne", f"{df['Consommation_kWh'].mean():.2f} kWh", "⚡")
        kpi3.metric("Délestage Moyen", f"{df['Heures_Delestage'].mean():.1f} h", "-h", delta_color="inverse")

    col_form, col_viz = st.columns([1, 2])
    
    with col_form:
        st.markdown("### 📝 Formulaire de Saisie")
        with st.form("form_bowa", clear_on_submit=True):
            quartier = st.text_input("Quartier / Localité")
            conso = st.number_input("Consommation mesurée (kWh)", min_value=0.0, help="Entrez la valeur lue sur le compteur")
            heures = st.number_input("Heures de délestage subies", min_value=0)
            facture = st.number_input("Montant de la dernière facture (CFA)", min_value=0)
            type_abo = st.selectbox("Type d'abonnement", ["Social", "Domestique", "Professionnel"])
            
            submit = st.form_submit_button("Enregistrer les données")
            if submit:
                if quartier:
                    gd.sauvegarder_donnee({
                        "Quartier": quartier, "Consommation_kWh": conso,
                        "Heures_Delestage": heures, "Montant_Facture": facture,
                        "Type_Abonnement": type_abo
                    })
                    st.balloons()
                    st.success(f"Données de {quartier} ajoutées avec succès !")
                else:
                    st.error("Veuillez entrer un nom de quartier.")

    with col_viz:
        st.markdown("### 📈 Aperçu Graphique")
        if not df.empty:
            fig = px.sunburst(df, path=['Type_Abonnement', 'Quartier'], values='Consommation_kWh',
                              title="Répartition de la consommation par type et quartier")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("En attente de données pour générer les graphiques...")

elif menu == "📊 Analyses IA (EC2)":
    st.markdown("### 🧠 Intelligence Artificielle & Statistiques")
    
    if len(df) >= 3:
        tab1, tab2, tab3 = st.tabs(["📉 Régression Facture", "🔮 PCA (Dimensions)", "🧩 Clustering"])
        
        with tab1:
            model, score = md.executer_regression(df)
            st.metric("Précision du Modèle (R²)", f"{score*100:.1f}%")
            st.info("Ce modèle prédit le montant de la facture en fonction de la consommation et du délestage.")
            fig_reg = px.scatter(df, x="Consommation_kWh", y="Montant_Facture", trendline="ols", 
                                 title="Corrélation Conso / Facture")
            st.plotly_chart(fig_reg)
            
        with tab2:
            comp, var = md.executer_pca(df)
            if comp is not None:
                st.write(f"**Variance conservée :** {sum(var)*100:.1f}%")
                fig_pca = px.scatter(x=comp[:,0], y=comp[:,1], color=df['Type_Abonnement'],
                                     title="Projection PCA des profils énergétiques",
                                     labels={'x': 'Composante 1', 'y': 'Composante 2'})
                st.plotly_chart(fig_pca)

        with tab3:
            df['Cluster'] = md.executer_clustering(df).astype(str)
            st.write("Le K-Means a identifié 3 segments de consommateurs :")
            fig_cluster = px.scatter(df, x="Consommation_kWh", y="Heures_Delestage", 
                                     color="Cluster", size="Montant_Facture",
                                     hover_data=['Quartier'])
            st.plotly_chart(fig_cluster)
    else:
        st.warning("⚠️ L'analyse IA nécessite au moins 3 enregistrements dans la base.")

elif menu == "📂 Historique & Export":
    st.markdown("### 📋 Base de Données Complète")
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger le rapport CSV",
        data=csv,
        file_name=f"rapport_bowa_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )