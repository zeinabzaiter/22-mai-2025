import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Surveillance RAM - Staph aureus", layout="wide")

# -------- Chargement des données --------
@st.cache_data
def load_data():
    staph_data = pd.read_excel("staph aureus hebdomadaire excel.xlsx")
    bacteries_list = pd.read_excel("TOUS les bacteries a etudier.xlsx")
    tests_semaine = pd.read_csv("tests_par_semaine_antibiotiques_2024.csv")
    phenotypes = pd.read_excel("staph_aureus_pheno_final.xlsx")
    other_ab = pd.read_excel("other Antibiotiques staph aureus.xlsx")
    return staph_data, bacteries_list, tests_semaine, phenotypes, other_ab

staph_data, bacteries_list, tests_semaine, phenotypes, other_ab = load_data()

# -------- Mise en page de l'application --------
st.title("Surveillance Dynamique de la Résistance aux Antimicrobiens")
st.markdown("""
Bienvenue dans le tableau de bord de suivi de la résistance bactérienne pour l'année 2024. Utilisez les onglets ci-dessous pour naviguer.
""")

# -------- Menu principal --------
tab_names = ["Vue générale", "Staph aureus - Phénotypes", "Staph aureus - Antibiotiques", 
             "Staph aureus - Autres AB", "Alertes par Service"]
tabs = st.tabs(tab_names)

# Onglet 1: Vue générale
with tabs[0]:
    st.subheader("Bactéries suivies en 2024")
    st.dataframe(bacteries_list)
    st.markdown("Cliquez sur les onglets suivants pour explorer les données spécifiques à Staphylococcus aureus.")

# Onglet 2: Phénotypes Staph aureus
with tabs[1]:
    st.subheader("Évolution des Phénotypes - Staphylococcus aureus")
    pheno_columns = [col for col in phenotypes.columns if col.lower() not in ['semaine', 'week']]
    selected_pheno = st.selectbox("Choisir un phénotype", pheno_columns)
    try:
        col_values = pd.to_numeric(phenotypes[selected_pheno], errors='coerce').dropna()
        Q1 = col_values.quantile(0.25)
        Q3 = col_values.quantile(0.75)
        IQR = Q3 - Q1
        tukey_threshold = Q3 + 1.5 * IQR
        phenotypes['Alarme'] = pd.to_numeric(phenotypes[selected_pheno], errors='coerce') > tukey_threshold
        fig = px.line(phenotypes, x='Semaine', y=selected_pheno, title=f"% Résistance - {selected_pheno}",
                     markers=True, labels={selected_pheno: "% de résistance"},
                     hover_data={"Semaine": True, selected_pheno: True})
        alertes = phenotypes[phenotypes['Alarme'] == True]
        fig.add_scatter(x=alertes['Semaine'], y=alertes[selected_pheno], mode='markers',
                        marker=dict(color='red', size=10), name='Alarme')
        st.plotly_chart(fig)
        st.markdown(f"Seuil d'alerte (règle de Tukey) pour {selected_pheno} : **{tukey_threshold:.2f}%**")
    except Exception as e:
        st.error(f"Erreur lors du traitement du phénotype {selected_pheno} : {e}")
