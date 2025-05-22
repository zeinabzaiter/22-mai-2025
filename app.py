import streamlit as st
import pandas as pd
import plotly.express as px

# ✅ Doit être ici, immédiatement après les imports !
st.set_page_config(page_title="Surveillance RAM - Staph aureus", layout="wide")

@st.cache_data
def load_data():
    ...


def load_data():
    staph_data = pd.read_excel("staph aureus hebdomadaire excel.xlsx")
    bacteries_list = pd.read_excel("TOUS les bacteries a etudier.xlsx")
    tests_semaine = pd.read_csv("tests_par_semaine_antibiotiques_2024.csv")
    phenotypes = pd.read_excel("staph_aureus_pheno_final.xlsx")
    other_ab = pd.read_excel("other Antibiotiques staph aureus.xlsx")
    return staph_data, bacteries_list, tests_semaine, phenotypes, other_ab

staph_data, bacteries_list, tests_semaine, phenotypes, other_ab = load_data()

# -------- Mise en page de l'application --------
st.set_page_config(page_title="Surveillance RAM - Staph aureus", layout="wide")
st.title("Surveillance Dynamique de la Résistance aux Antimicrobiens")
st.markdown("""
Bienvenue dans le tableau de bord de suivi de la résistance bactérienne pour l'année 2024. Utilisez les onglets ci-dessous pour naviguer.
""")

# -------- Menu principal --------
tabs = st.tabs(["Vue générale", "Staph aureus - Phénotypes", "Staph aureus - Antibiotiques", 
                "Staph aureus - Autres AB", "Alertes par Service"])

# Onglet 1: Vue générale
with tabs[0]:
    st.subheader("Bactéries suivies en 2024")
    st.dataframe(bacteries_list)
    st.markdown("Cliquez sur les onglets suivants pour explorer les données spécifiques à Staphylococcus aureus.")

# Onglet 2: Phénotypes Staph aureus
with tabs[1]:
    st.subheader("Évolution des Phénotypes - Staphylococcus aureus")
    pheno_columns = [col for col in phenotypes.columns if col not in ['Semaine']]
    selected_pheno = st.selectbox("Choisir un phénotype", pheno_columns)

    # Calcul du seuil de Tukey
    Q1 = phenotypes[selected_pheno].quantile(0.25)
    Q3 = phenotypes[selected_pheno].quantile(0.75)
    IQR = Q3 - Q1
    tukey_threshold = Q3 + 1.5 * IQR

    # Ajout colonne alarme
    phenotypes['Alarme'] = phenotypes[selected_pheno] > tukey_threshold

    fig = px.line(
        phenotypes,
        x='Semaine',
        y=selected_pheno,
        title=f"% Résistance - {selected_pheno}",
        markers=True,
        labels={selected_pheno: "% de résistance"},
        hover_data={"Semaine": True, selected_pheno: True}
    )

    # Ajouter les points d’alerte en rouge foncé
    alertes = phenotypes[phenotypes['Alarme'] == True]
    fig.add_scatter(
        x=alertes['Semaine'],
        y=alertes[selected_pheno],
        mode='markers',
        marker=dict(color='red', size=10),
        name='Alarme'
    )

    st.plotly_chart(fig)
    st.markdown(f"Seuil d'alerte (règle de Tukey) pour {selected_pheno} : **{tukey_threshold:.2f}%**")
... # contenu précédent intact ...

# Onglet 4: Autres Antibiotiques Staph aureus
with tabs[3]:
    st.subheader("Autres Antibiotiques - Staphylococcus aureus")
    other_ab_columns = [col for col in other_ab.columns if col not in ['Semaine']]
    selected_other_ab = st.selectbox("Choisir un antibiotique parmi les autres", other_ab_columns)

    # Calcul du seuil de Tukey
    Q1 = other_ab[selected_other_ab].quantile(0.25)
    Q3 = other_ab[selected_other_ab].quantile(0.75)
    IQR = Q3 - Q1
    tukey_threshold = Q3 + 1.5 * IQR

    # Détection des alarmes
    other_ab['Alarme'] = other_ab[selected_other_ab] > tukey_threshold

    fig_other = px.line(
        other_ab,
        x='Semaine',
        y=selected_other_ab,
        title=f"% Résistance - {selected_other_ab}",
        markers=True,
        labels={selected_other_ab: "% de résistance"},
        hover_data={"Semaine": True, selected_other_ab: True}
    )

    alertes_other = other_ab[other_ab['Alarme'] == True]
    fig_other.add_scatter(
        x=alertes_other['Semaine'],
        y=alertes_other[selected_other_ab],
        mode='markers',
        marker=dict(color='red', size=10),
        name='Alarme'
    )

    st.plotly_chart(fig_other)
    st.markdown(f"Seuil d'alerte (règle de Tukey) pour {selected_other_ab} : **{tukey_threshold:.2f}%**")
... # contenu précédent intact ...

# Onglet 5: Alertes par Service
with tabs[4]:
    st.subheader("Alertes par Service - Staphylococcus aureus")
    staph_data['DATE_PRELEVEMENT'] = pd.to_datetime(staph_data['DATE_PRELEVEMENT'], errors='coerce')
    staph_data['Semaine'] = staph_data['DATE_PRELEVEMENT'].dt.isocalendar().week

    selected_ab_service = st.selectbox("Choisir un antibiotique à analyser", tests_semaine.columns[1:])

    # Calcul des % par semaine et service
    grouped = staph_data.groupby(['Semaine', 'DEMANDEUR'])[selected_ab_service].apply(lambda x: (x == 'R').mean() * 100).reset_index()
    grouped.columns = ['Semaine', 'Service', 'Resistance (%)']

    # Seuil d'alerte Tukey
    Q1 = grouped['Resistance (%)'].quantile(0.25)
    Q3 = grouped['Resistance (%)'].quantile(0.75)
    IQR = Q3 - Q1
    tukey_threshold = Q3 + 1.5 * IQR
    grouped['Alarme'] = grouped['Resistance (%)'] > tukey_threshold

    # Affichage
    st.markdown("### Graphique interactif par service")
    fig_alertes = px.scatter(
        grouped,
        x='Semaine',
        y='Resistance (%)',
        color='Service',
        symbol='Alarme',
        size=grouped['Alarme'].apply(lambda x: 12 if x else 6),
        hover_data=['Service', 'Resistance (%)'],
        title=f"Alertes de résistance pour {selected_ab_service} par service"
    )

    st.plotly_chart(fig_alertes)
    st.markdown(f"Seuil d'alerte (Tukey) : **{tukey_threshold:.2f}%**")

    st.markdown("### Liste des services avec alarme")
    alertes_services = grouped[grouped['Alarme'] == True]
    st.dataframe(alertes_services)

# Onglet 3: Antibiotiques Staph aureus
with tabs[2]:
    st.subheader("Évolution des Résistances aux Antibiotiques - Staphylococcus aureus")
    ab_columns = [col for col in tests_semaine.columns if col not in ['Semaine']]
    selected_ab = st.selectbox("Choisir un antibiotique", ab_columns)

    # Calcul du seuil de Tukey
    Q1 = tests_semaine[selected_ab].quantile(0.25)
    Q3 = tests_semaine[selected_ab].quantile(0.75)
    IQR = Q3 - Q1
    tukey_threshold = Q3 + 1.5 * IQR

    # Détection des alarmes selon Tukey ou règle stricte pour VAN
    if selected_ab.upper().startswith("VAN"):
        tests_semaine['Alarme'] = tests_semaine[selected_ab] > 0  # Alarme dès 1 cas
    else:
        tests_semaine['Alarme'] = tests_semaine[selected_ab] > tukey_threshold

    fig_ab = px.line(
        tests_semaine,
        x='Semaine',
        y=selected_ab,
        title=f"% Résistance - {selected_ab}",
        markers=True,
        labels={selected_ab: "% de résistance"},
        hover_data={"Semaine": True, selected_ab: True}
    )

    # Ajouter les points d’alarme
    alertes_ab = tests_semaine[tests_semaine['Alarme'] == True]
    fig_ab.add_scatter(
        x=alertes_ab['Semaine'],
        y=alertes_ab[selected_ab],
        mode='markers',
        marker=dict(color='red', size=10),
        name='Alarme'
    )

    st.plotly_chart(fig_ab)
    seuil_info = "1 cas = alarme" if selected_ab.upper().startswith("VAN") else f"Seuil Tukey : **{tukey_threshold:.2f}%**"
    st.markdown(f"Critère d'alarme pour {selected_ab} : {seuil_info}")
