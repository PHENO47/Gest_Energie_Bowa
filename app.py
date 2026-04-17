
import streamlit as st
import gestion_data as gd
import modeles as md
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Gest_Energie_Bowa", page_icon="⚡", layout="wide")
gd.initialiser_csv()

st.title("⚡ Gest_Energie_Bowa : Analyse Energetique")
st.markdown("---")

# Sidebar
st.sidebar.header("Menu Principal")
menu = st.sidebar.radio("Navigation", ["Collecte & Dashboard", "Analyse Avancee (EC2)", "Historique"])

df = gd.charger_donnees()

# --- PÉPITE 1 : INDICATEURS EN TEMPS RÉEL (Dashboard) ---
if not df.empty:
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.metric("Total Collecte", f"{len(df)} entrees")
    with col_kpi2:
        st.metric("Conso Moyenne", f"{df['Consommation_kWh'].mean():.2f} kWh")
    with col_kpi3:
        st.metric("Delestage Moyen", f"{df['Heures_Delestage'].mean():.1f} h")

if menu == "Collecte & Dashboard":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Saisie des donnees")
        with st.form("form_bowa"):
            quartier = st.text_input("Quartier")
            conso = st.number_input("Consommation (kWh)", min_value=0.0)
            heures = st.number_input("Heures de delestage", min_value=0)
            facture = st.number_input("Montant Facture (CFA)", min_value=0)
            type_abo = st.selectbox("Abonnement", ["Social", "Domestique", "Professionnel"])
            
            if st.form_submit_button("💾 Enregistrer"):
                gd.sauvegarder_donnee({
                    "Quartier": quartier, "Consommation_kWh": conso,
                    "Heures_Delestage": heures, "Montant_Facture": facture,
                    "Type_Abonnement": type_abo
                })
                st.success("Données enregistrées !")
                st.rerun()

    with col2:
        st.subheader("Visualisation Rapide")
        if not df.empty:
            fig = px.bar(df, x="Quartier", y="Consommation_kWh", color="Type_Abonnement", barmode="group")
            st.plotly_chart(fig, use_container_width=True)

elif menu == "Analyse Avancee (EC2)":
    st.subheader("Analyses Statistiques et IA")
    if len(df) >= 3:
        # PÉPITE 2 : ORGANISATION PAR ONGLETS POUR PLUS DE CLARTÉ
        t1, t2, t3 = st.tabs(["Regression", "Reduction de Dimension", "Classification"])
        
        with t1:
            model, score = md.executer_regression(df)
            st.write(f"**Precision du modele (R²) :** {score:.2f}")
            st.info("Ce modele analyse l'impact du delestage sur le montant des factures.")
            
        with t2:
            comp, var = md.executer_pca(df)
            if comp is not None:
                st.write(f"Variance expliquee : {sum(var)*100:.1f}%")
                fig_pca = px.scatter(x=comp[:,0], y=comp[:,1], title="Projection PCA des donnees")
                st.plotly_chart(fig_pca)

        with t3:
            df['Groupe'] = md.executer_clustering(df).astype(str)
            fig_cluster = px.scatter(df, x="Consommation_kWh", y="Montant_Facture", color="Groupe", symbol="Type_Abonnement")
            st.plotly_chart(fig_cluster)
    else:
        st.warning("⚠️ Collectez au moins 3 enregistrements pour activer l'IA.")

elif menu == "Historique":
    st.subheader("Gestion des archives")
    st.dataframe(df)
    
    # PÉPITE 3 : BOUTON DE TÉLÉCHARGEMENT
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Telécharger le fichier CSV", data=csv, file_name="export_bowa.csv", mime="text/csv")
