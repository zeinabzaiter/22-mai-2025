... # contenu précédent intact ...

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
        Q1 = phenotypes[selected_pheno].astype(float).quantile(0.25)
        Q3 = phenotypes[selected_pheno].astype(float).quantile(0.75)
        IQR = Q3 - Q1
        tukey_threshold = Q3 + 1.5 * IQR

        phenotypes['Alarme'] = phenotypes[selected_pheno].astype(float) > tukey_threshold

        fig = px.line(
            phenotypes,
            x='Semaine',
            y=selected_pheno,
            title=f"% Résistance - {selected_pheno}",
            markers=True,
            labels={selected_pheno: "% de résistance"},
            hover_data={"Semaine": True, selected_pheno: True}
        )

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

    except Exception as e:
        st.error(f"Erreur lors du traitement du phénotype {selected_pheno} : {e}")


# Onglet 3: Antibiotiques Staph aureus
with tabs[2]:
    st.subheader("Évolution des Résistances aux Antibiotiques - Staphylococcus aureus")
    ab_columns = [col for col in tests_semaine.columns if col.lower() not in ['semaine', 'week']]
    selected_ab = st.selectbox("Choisir un antibiotique", ab_columns)

    try:
        Q1 = tests_semaine[selected_ab].astype(float).quantile(0.25)
        Q3 = tests_semaine[selected_ab].astype(float).quantile(0.75)
        IQR = Q3 - Q1
        tukey_threshold = Q3 + 1.5 * IQR

        if selected_ab.upper().startswith("VAN"):
            tests_semaine['Alarme'] = tests_semaine[selected_ab].astype(float) > 0
        else:
            tests_semaine['Alarme'] = tests_semaine[selected_ab].astype(float) > tukey_threshold

        fig_ab = px.line(
            tests_semaine,
            x='Semaine',
            y=selected_ab,
            title=f"% Résistance - {selected_ab}",
            markers=True,
            labels={selected_ab: "% de résistance"},
            hover_data={"Semaine": True, selected_ab: True}
        )

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

    except Exception as e:
        st.error(f"Erreur lors du traitement de l'antibiotique {selected_ab} : {e}")

# Onglet 4: Autres Antibiotiques Staph aureus
with tabs[3]:
    st.subheader("Autres Antibiotiques - Staphylococcus aureus")
    other_ab_columns = [col for col in other_ab.columns if col.lower() not in ['semaine', 'week']]
    selected_other_ab = st.selectbox("Choisir un antibiotique parmi les autres", other_ab_columns)

    try:
        Q1 = other_ab[selected_other_ab].astype(float).quantile(0.25)
        Q3 = other_ab[selected_other_ab].astype(float).quantile(0.75)
        IQR = Q3 - Q1
        tukey_threshold = Q3 + 1.5 * IQR

        other_ab['Alarme'] = other_ab[selected_other_ab].astype(float) > tukey_threshold

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

    except Exception as e:
        st.error(f"Erreur lors du traitement de l'antibiotique {selected_other_ab} : {e}")
# Onglet 5: Alertes par Service
with tabs[4]:
    st.subheader("Alertes par Service - Staphylococcus aureus")
    staph_data['DATE_PRELEVEMENT'] = pd.to_datetime(staph_data['DATE_PRELEVEMENT'], errors='coerce')
    staph_data['Semaine'] = staph_data['DATE_PRELEVEMENT'].dt.isocalendar().week

    service_columns = [col for col in tests_semaine.columns if col.lower() not in ['semaine', 'week']]
    selected_ab_service = st.selectbox("Choisir un antibiotique à analyser", service_columns)

    try:
        grouped = staph_data.groupby(['Semaine', 'DEMANDEUR'])[selected_ab_service] \
            .apply(lambda x: (x == 'R').mean() * 100).reset_index()
        grouped.columns = ['Semaine', 'Service', 'Resistance (%)']

        Q1 = grouped['Resistance (%)'].quantile(0.25)
        Q3 = grouped['Resistance (%)'].quantile(0.75)
        IQR = Q3 - Q1
        tukey_threshold = Q3 + 1.5 * IQR
        grouped['Alarme'] = grouped['Resistance (%)'] > tukey_threshold

        st.markdown("### Graphique interactif par service")
        fig_alertes = px.scatter(grouped, x='Semaine', y='Resistance (%)', color='Service', symbol='Alarme',
                                 size=grouped['Alarme'].apply(lambda x: 12 if x else 6),
                                 hover_data=['Service', 'Resistance (%)'],
                                 title=f"Alertes de résistance pour {selected_ab_service} par service")

        st.plotly_chart(fig_alertes)
        st.markdown(f"Seuil d'alerte (Tukey) : **{tukey_threshold:.2f}%**")

        st.markdown("### Liste des services avec alarme")
        alertes_services = grouped[grouped['Alarme'] == True]
        st.dataframe(alertes_services)

    except Exception as e:
        st.error(f"Erreur lors de l'analyse des alertes par service pour {selected_ab_service} : {e}")
