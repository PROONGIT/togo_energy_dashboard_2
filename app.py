import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    load_wb, load_ges_2018, load_temperatures, load_renewables_combustible,
    load_co2_power_long, load_forets_table, load_forets_geojson,
    inject_css, kpi_card, constat_box, section_tag, analysis_caption,
    REGION_COLORS, VILLES_ORDRE, VILLE_COLORS, VILLE_COORDS,
    TOGO_GREEN, TOGO_YELLOW, TOGO_RED,
)

st.set_page_config(
    page_title="Énergie & Environnement au Togo",
    page_icon="⚡",
    layout="wide",
)
inject_css()

# ---------- Données ----------
wb = load_wb()
ges = load_ges_2018()
temp = load_temperatures()
renew_combust = load_renewables_combustible()
co2_long = load_co2_power_long()
forets = load_forets_table()
forets_geojson = load_forets_geojson()

# ---------- En-tête ----------
st.caption(
    
    "Auteur : AZIAGBEDO KOKOU SODJINE, Ingénieur en Sciences informatiques, Sécurité informatique - Data & IA"
)

st.markdown('<div class="top-flag-bar"></div>', unsafe_allow_html=True)
st.title("⚡ Énergie, Climat & Forêts au Togo")
st.markdown(
    '<p class="subtitle">Électrifier les villages, développer les énergies propres et protéger les forêts — '
    'cap 2030 : accès universel à l\'électricité</p>',
    unsafe_allow_html=True
)

# ---------- KPIs globaux ----------
last = wb.dropna(subset=["elec_access_national"]).iloc[-1]
last_year = int(last["year"])
c1, c2, c3, c4, c5 = st.columns(5)
kpi_card(c1, "Accès électricité national", f"{last['elec_access_national']:.1f}%", TOGO_GREEN, f"Données {last_year}")
kpi_card(c2, "Accès électricité rural", f"{wb.dropna(subset=['elec_access_rural']).iloc[-1]['elec_access_rural']:.1f}%", TOGO_RED, "Le maillon faible")
kpi_card(c3, "Accès électricité urbain", f"{wb.dropna(subset=['elec_access_urban']).iloc[-1]['elec_access_urban']:.1f}%", TOGO_GREEN)
kpi_card(c4, "Superficie forestière", f"{wb.dropna(subset=['forest_area_pct']).iloc[-1]['forest_area_pct']:.1f}%", TOGO_YELLOW, "% du territoire")
kpi_card(c5, "Forêts classées cartographiées", f"{len(forets)}", TOGO_GREEN, "Sur tout le pays")

st.write("")
tabs = st.tabs([
    "🔌 Accès à l'électricité",
    "🔥 Énergie des ménages",
    "🏭 Émissions polluantes",
    "🌡️ Climat",
    "🌳 Aires protégées",
    "💡 Recommandations",
])

# ================= ONGLET 1 : ACCES ELECTRICITE =================
with tabs[0]:
    section_tag("Objectif 1 — comparer villes et villages, mesurer la fiabilité du réseau")
    st.subheader("Accès à l'électricité : un écart ville-village qui reste ouvert")

    df_e = wb.dropna(subset=["elec_access_national"], how="all")
    gap_row = df_e.dropna(subset=["elec_access_urban", "elec_access_rural"]).iloc[-1]
    gap_first = df_e.dropna(subset=["elec_access_urban", "elec_access_rural"]).iloc[0]
    ecart_now = gap_row["elec_access_urban"] - gap_row["elec_access_rural"]
    ecart_first = gap_first["elec_access_urban"] - gap_first["elec_access_rural"]

    col1, col2 = st.columns(2)
    with col1:
        constat_box(
            "📍 État des lieux",
            f"En {int(gap_row['year'])}, <b>{gap_row['elec_access_urban']:.1f}%</b> des citadins ont l'électricité "
            f"contre seulement <b>{gap_row['elec_access_rural']:.1f}%</b> en zone rurale — un écart de "
            f"<b>{ecart_now:.0f} points</b>. Il y a {int(gap_row['year'])-int(gap_first['year'])} ans, cet écart "
            f"était de {ecart_first:.0f} points : la fracture s'est {'creusée' if ecart_now > ecart_first else 'réduite'} "
            "plus qu'elle ne s'est résorbée.",
            kind="critique"
        )
    with col2:
        constat_box(
            "🎯 Vers l'objectif 2030",
            f"Au rythme actuel, l'accès national progresse d'environ "
            f"{(df_e['elec_access_national'].iloc[-1]-df_e['elec_access_national'].dropna().iloc[0])/(int(df_e.dropna(subset=['elec_access_national']).iloc[-1]['year'])-int(df_e.dropna(subset=['elec_access_national']).iloc[0]['year'])):.1f} "
            "points par an. À ce rythme, l'accès universel en zone rurale ne sera pas atteint d'ici 2030 sans "
            "accélération — d'où l'urgence d'une stratégie hors-réseau (solaire décentralisé) pour les villages.",
            kind="alerte"
        )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_e["year"], y=df_e["elec_access_urban"], name="Urbain",
                              line=dict(color=TOGO_GREEN, width=3)))
    fig.add_trace(go.Scatter(x=df_e["year"], y=df_e["elec_access_rural"], name="Rural",
                              line=dict(color=TOGO_RED, width=3)))
    fig.add_trace(go.Scatter(x=df_e["year"], y=df_e["elec_access_national"], name="National",
                              line=dict(color="#666666", width=2, dash="dot")))
    fig.add_hline(y=100, line_dash="dash", line_color="lightgray",
                  annotation_text="Objectif 2030 : 100%", annotation_position="top left")
    fig.update_layout(
        yaxis_title="% de la population avec accès", xaxis_title="Année",
        legend=dict(orientation="h", y=1.1), height=430,
        hovermode="x unified", plot_bgcolor="white"
    )
    st.plotly_chart(fig, use_container_width=True)
    analysis_caption(
        "<b>Lecture :</b> la courbe verte (urbain) progresse de façon quasi linéaire et approche les 100%, "
        "tandis que la courbe rouge (rural) stagne autour de 20-26% depuis 2013. La ligne pointillée (national) "
        "est donc tirée vers le haut par les villes, ce qui masque, à l'échelle nationale, l'ampleur du retard "
        "des campagnes — le cœur du problème posé par ce projet."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Fiabilité du réseau : entreprises touchées par des coupures**")
        df_out = wb.dropna(subset=["firms_outages_pct"])[["year", "firms_outages_pct"]]
        fig2 = px.bar(df_out, x="year", y="firms_outages_pct",
                      labels={"firms_outages_pct": "% d'entreprises touchées", "year": "Année"},
                      color_discrete_sequence=[TOGO_RED])
        fig2.update_layout(height=340, plot_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)
        if not df_out.empty:
            analysis_caption(
                f"<b>{df_out.iloc[-1]['firms_outages_pct']:.0f}% des entreprises</b> déclarent être affectées par "
                "des coupures — un frein direct à la productivité et à la confiance dans le réseau, y compris là "
                "où l'électricité est disponible."
            )

    with col2:
        st.markdown("**Délai de raccordement électrique**")
        df_conn = wb.dropna(subset=["elec_connection_days"])[["year", "elec_connection_days"]]
        if not df_conn.empty:
            fig3 = px.bar(df_conn, x="year", y="elec_connection_days",
                          labels={"elec_connection_days": "Jours nécessaires", "year": "Année"},
                          color_discrete_sequence=[TOGO_YELLOW])
            fig3.update_layout(height=340, plot_bgcolor="white")
            st.plotly_chart(fig3, use_container_width=True)
            analysis_caption(
                f"Il faut environ <b>{df_conn.iloc[-1]['elec_connection_days']:.0f} jours</b> pour obtenir un "
                "raccordement — un délai qui décourage les ménages et petites entreprises rurales de s'engager "
                "dans la démarche, même quand le réseau est physiquement proche."
            )
        else:
            st.info("Données de délai de raccordement non disponibles sur la période.")

# ================= ONGLET 2 : ENERGIE DES MENAGES =================
with tabs[1]:
    section_tag("Objectif 2 — dépendance au bois/charbon et impact sur les forêts")
    st.subheader("Cuisson des ménages : une dépendance au bois-énergie qui pèse sur la forêt")

    df_cook = wb.dropna(subset=["cook_wood_pct"], how="all")
    if not df_cook.empty:
        last_cook = df_cook.iloc[-1]
        bois_charbon = last_cook["cook_wood_pct"] + last_cook["cook_charcoal_pct"]

        col1, col2 = st.columns(2)
        with col1:
            constat_box(
                "📍 État des lieux",
                f"En {int(last_cook['year'])}, <b>{bois_charbon:.0f}% des ménages togolais</b> cuisinent encore "
                f"au bois ou au charbon de bois, contre seulement <b>{last_cook['cook_lpg_pct']:.1f}%</b> au gaz. "
                "Cette dépendance est la première cause de pression sur les forêts, bien avant l'exploitation "
                "commerciale du bois.",
                kind="critique"
            )
        with col2:
            df_forest_tmp = wb.dropna(subset=["forest_area_sqkm"])[["year", "forest_area_sqkm"]]
            perte_tmp = df_forest_tmp.iloc[0]["forest_area_sqkm"] - df_forest_tmp.iloc[-1]["forest_area_sqkm"]
            constat_box(
                "🌳 Lien direct avec la forêt",
                f"Sur la même période, le pays a perdu <b>{perte_tmp:,.0f} km²</b> de couvert forestier. "
                "Le bois de chauffe et le charbon de bois ne sont pas la seule cause du recul forestier "
                "(agriculture, urbanisation y contribuent aussi), mais ils en sont un facteur structurant, "
                "renouvelé chaque jour par des millions de foyers.",
                kind="alerte"
            )

        cook_cols = ["cook_wood_pct", "cook_charcoal_pct", "cook_lpg_pct", "cook_electricity_pct"]
        labels = {"cook_wood_pct": "Bois", "cook_charcoal_pct": "Charbon de bois",
                  "cook_lpg_pct": "Gaz (LPG)", "cook_electricity_pct": "Électricité"}
        melted = df_cook.melt(id_vars="year", value_vars=cook_cols, var_name="combustible", value_name="pct")
        melted["combustible"] = melted["combustible"].map(labels)
        fig4 = px.bar(melted, x="year", y="pct", color="combustible", barmode="group",
                      color_discrete_map={"Bois": "#8c510a", "Charbon de bois": "#333333",
                                          "Gaz (LPG)": TOGO_GREEN, "Électricité": "#0072B2"},
                      labels={"pct": "% des ménages", "year": "Année", "combustible": "Combustible principal"})
        fig4.update_layout(height=400, plot_bgcolor="white", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig4, use_container_width=True)
        analysis_caption(
            "<b>Lecture :</b> les deux seules années mesurées (2014 et 2017) montrent une structure de cuisson "
            "quasiment inchangée — le bois et le charbon dominent largement, sans signe de bascule spontanée "
            "vers le gaz ou l'électricité. Sans intervention volontariste (subvention, distribution de foyers "
            "améliorés), cette structure a peu de raisons d'évoluer d'elle-même."
        )
    else:
        st.info("Données de combustible de cuisson limitées à 2 points de mesure (2014, 2017).")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Accès aux modes de cuisson propres : ville vs village**")
        df_clean = wb.dropna(subset=["clean_cooking_national"], how="all")
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(x=df_clean["year"], y=df_clean["clean_cooking_urban"], name="Urbain", line=dict(color=TOGO_GREEN)))
        fig5.add_trace(go.Scatter(x=df_clean["year"], y=df_clean["clean_cooking_rural"], name="Rural", line=dict(color=TOGO_RED)))
        fig5.update_layout(yaxis_title="% population", height=360, legend=dict(orientation="h", y=1.12), plot_bgcolor="white")
        st.plotly_chart(fig5, use_container_width=True)
        if not df_clean.empty:
            analysis_caption(
                "Même schéma que pour l'électricité : la cuisson propre progresse en ville mais reste marginale "
                "en zone rurale — les deux fractures (électrique et énergétique domestique) se superposent sur "
                "les mêmes territoires."
            )

    with col2:
        st.markdown("**Recul de la superficie forestière**")
        df_forest = wb.dropna(subset=["forest_area_sqkm"])[["year", "forest_area_sqkm"]]
        fig6 = px.area(df_forest, x="year", y="forest_area_sqkm",
                       labels={"forest_area_sqkm": "Superficie (km²)", "year": "Année"},
                       color_discrete_sequence=[TOGO_GREEN])
        fig6.update_layout(height=360, plot_bgcolor="white")
        st.plotly_chart(fig6, use_container_width=True)
        perte = df_forest.iloc[0]["forest_area_sqkm"] - df_forest.iloc[-1]["forest_area_sqkm"]
        analysis_caption(
            f"Perte de <b>{perte:,.0f} km²</b> de forêt entre {int(df_forest.iloc[0]['year'])} et "
            f"{int(df_forest.iloc[-1]['year'])} — une tendance de fond continue, sans palier ni inversion visible."
        )

# ================= ONGLET 3 : EMISSIONS =================
with tabs[2]:
    section_tag("Objectif 3 — bilan des émissions polluantes par secteur")
    st.subheader("Émissions de gaz à effet de serre : l'énergie n'est pas le premier poste")

    ges_total = ges[(ges["secteur"] != "Total") & (ges["gaz"] == "Total")].sort_values("value", ascending=False)
    top_secteur = ges_total.iloc[0]
    energie_val = ges_total[ges_total["secteur"] == "Energie"]["value"].values[0]
    energie_pct = energie_val / ges_total["value"].sum() * 100

    col1, col2 = st.columns(2)
    with col1:
        constat_box(
            "📍 État des lieux (bilan officiel 2018)",
            f"Le secteur <b>{top_secteur['secteur']}</b> domine largement le bilan national avec "
            f"<b>{top_secteur['value']:.0f} Gg</b> d'émissions, loin devant l'Énergie "
            f"({energie_val:.0f} Gg, soit {energie_pct:.1f}% du total). Contrairement à une idée reçue, "
            "ce n'est donc pas la production d'électricité qui pèse le plus sur le climat togolais.",
            kind="positif"
        )
    with col2:
        constat_box(
            "🔄 Le vrai lien avec l'énergie",
            "Le poids de l'AFAT (Agriculture, Foresterie, Affectation des Terres) s'explique en grande partie par "
            "le recul forestier documenté dans l'onglet précédent — largement alimenté par la collecte de "
            "bois-énergie. L'énergie et les forêts ne sont donc pas deux sujets séparés : le premier nourrit "
            "la pression sur le second.",
            kind="alerte"
        )

    fig7 = px.bar(ges_total, x="value", y="secteur", orientation="h",
                  labels={"value": "Émissions (Gg)", "secteur": ""},
                  color="secteur",
                  color_discrete_sequence=[TOGO_GREEN, TOGO_YELLOW, "#F28C28", TOGO_RED])
    fig7.update_layout(height=320, showlegend=False, plot_bgcolor="white")
    st.plotly_chart(fig7, use_container_width=True)
    analysis_caption(
        "<b>Lecture :</b> classement des 4 secteurs (hors Total) par émissions totales en 2018. L'AFAT à lui "
        "seul dépasse la somme de tous les autres secteurs — un signal fort que la priorité climatique du Togo "
        "se joue autant dans les forêts et les champs que dans les centrales électriques."
    )

    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.markdown("**Répartition par type de gaz et par secteur**")
        ges_detail = ges[(ges["secteur"] != "Total") & (ges["gaz"] != "Total")]
        fig8 = px.bar(ges_detail, x="secteur", y="value", color="gaz", barmode="stack",
                      labels={"value": "Émissions (Gg)", "secteur": "", "gaz": "Gaz"},
                      color_discrete_map={"Dioxyde de carbone (CO2)": "#555555",
                                          "Méthane(CH4)": TOGO_GREEN,
                                          "Protoxyde d'azote (N2O)": TOGO_RED})
        fig8.update_layout(height=400, xaxis_tickangle=-15, plot_bgcolor="white")
        st.plotly_chart(fig8, use_container_width=True)
        analysis_caption(
            "L'AFAT se distingue par une forte composante <b>méthane (CH4)</b> — cohérent avec l'élevage et la "
            "décomposition de la matière organique — tandis que l'Énergie émet presque exclusivement du CO2, "
            "signature typique de la combustion."
        )

    with col2:
        st.markdown("**Évolution longue du CO₂ électrique**")
        fig9 = px.area(co2_long.dropna(), x="year", y="co2_power_industry_long",
                       labels={"co2_power_industry_long": "CO₂ (Mt CO2e)", "year": "Année"},
                       color_discrete_sequence=[TOGO_RED])
        fig9.update_layout(height=400, plot_bgcolor="white")
        st.plotly_chart(fig9, use_container_width=True)
        analysis_caption(
            "La hausse depuis 2014 reflète le développement du parc de production électrique national — un point "
            "de vigilance pour que l'électrification à venir privilégie des sources renouvelables plutôt que "
            "fossiles."
        )

# ================= ONGLET 4 : CLIMAT =================
with tabs[3]:
    section_tag("Objectif 4 — variations climatiques du Sud au Nord")
    st.subheader("Températures : un gradient Sud-Nord qui accentue les besoins en énergie")

    avg_max_by_ville = temp[temp["type_temp"] == "Températures maximales"].groupby("ville", observed=True)["value"].mean().reindex(VILLES_ORDRE)
    ecart_climat = avg_max_by_ville.max() - avg_max_by_ville.min()
    ville_plus_chaude = avg_max_by_ville.idxmax()
    ville_plus_fraiche = avg_max_by_ville.idxmin()

    col1, col2 = st.columns(2)
    with col1:
        constat_box(
            "📍 État des lieux",
            f"<b>{ville_plus_chaude}</b> affiche la température maximale moyenne la plus élevée "
            f"({avg_max_by_ville.max():.1f}°C), tandis que <b>{ville_plus_fraiche}</b> est la plus fraîche "
            f"({avg_max_by_ville.min():.1f}°C) — un écart de <b>{ecart_climat:.1f}°C</b> entre le Nord chaud "
            "et les zones les plus tempérées du pays.",
            kind="alerte"
        )
    with col2:
        constat_box(
            "🔗 Lien avec l'énergie",
            "Les zones les plus chaudes du Nord (Dapaong, Mango) cumulent le climat le plus rude, l'accès rural "
            "à l'électricité le plus faible et la couverture forestière classée la plus réduite (voir onglet "
            "Aires protégées) — une triple vulnérabilité qui doit orienter les priorités d'intervention.",
            kind="critique"
        )

    col1, col2 = st.columns([1, 3])
    with col1:
        type_temp = st.radio("Type de température", ["Températures maximales", "Températures minimales"])
        villes_sel = st.multiselect("Villes", VILLES_ORDRE, default=VILLES_ORDRE)

    with col2:
        df_t = temp[(temp["type_temp"] == type_temp) & (temp["ville"].isin(villes_sel))]
        fig10 = px.line(df_t, x="date", y="value", color="ville",
                        category_orders={"ville": VILLES_ORDRE},
                        labels={"value": "Température (°C)", "date": ""},
                        color_discrete_map=VILLE_COLORS)
        fig10.update_traces(line=dict(width=2))
        fig10.update_layout(height=420, legend=dict(orientation="h", y=1.18), plot_bgcolor="white")
        st.plotly_chart(fig10, use_container_width=True)
    analysis_caption(
        "<b>Lecture :</b> chaque ville a désormais une couleur unique et fortement contrastée (palette adaptée "
        "aux daltoniens) pour éviter toute confusion entre courbes voisines. Le cycle saisonnier est visible "
        "pour toutes les villes, mais le niveau moyen et l'amplitude diffèrent nettement entre le Sud côtier et "
        "les Savanes du Nord."
    )

    st.markdown("**Température moyenne par ville (Sud → Nord)**")
    avg_by_ville = temp[temp["type_temp"] == type_temp].groupby("ville", observed=True)["value"].mean().reindex(VILLES_ORDRE).reset_index()
    fig11 = px.bar(avg_by_ville, x="ville", y="value",
                   labels={"value": "Température moyenne (°C)", "ville": ""},
                   color="ville", color_discrete_map=VILLE_COLORS)
    fig11.update_layout(height=350, showlegend=False, plot_bgcolor="white")
    st.plotly_chart(fig11, use_container_width=True)
    analysis_caption(
        "Classées dans l'ordre géographique Sud → Nord, les villes montrent une hausse globale de la température "
        "en allant vers le Nord, cohérente avec le passage du climat subéquatorial côtier au climat soudanien "
        "plus sec des Savanes."
    )

# ================= ONGLET 5 : FORETS / CARTE =================
with tabs[4]:
    section_tag("Objectif 5 — cartographier les aires protégées")
    st.subheader("53 forêts classées face au climat et aux besoins énergétiques des villages")

    counts = forets["region"].value_counts().reindex(sorted(forets["region"].unique())).fillna(0)
    region_min = counts.idxmin()

    col1, col2 = st.columns(2)
    with col1:
        constat_box(
            "📍 État des lieux",
            f"Les 53 forêts classées sont très inégalement réparties : <b>{int(counts.max())} forêts</b> dans la "
            f"région la mieux dotée, contre seulement <b>{int(counts.min())} forêts</b> en <b>{region_min}</b> — "
            "la région pourtant la plus chaude et la plus vulnérable à la déforestation liée au bois-énergie.",
            kind="critique"
        )
    with col2:
        constat_box(
            "🗺️ Ce que montre la carte",
            "En superposant les 10 villes météo aux polygones forestiers, on visualise directement les zones où "
            "chaleur, dépendance au bois-énergie et faible couverture protégée se cumulent — ce sont les zones "
            "à cibler en priorité pour le reboisement et l'électrification.",
            kind="neutral"
        )

    col1, col2 = st.columns([1, 3])
    with col1:
        regions_sel = st.multiselect("Régions (forêts)", sorted(forets["region"].unique()),
                                      default=sorted(forets["region"].unique()))
        st.caption("🟩 Couleur des polygones = région (nuances de vert)")
        st.markdown("**Forêts classées par région**")
        for r, n in counts.items():
            couleur = REGION_COLORS.get(r, "#999999")
            st.markdown(
                f'<span style="color:{couleur}; font-size:1.1rem;">●</span> {r} : <b>{int(n)}</b> forêts',
                unsafe_allow_html=True
            )
        st.markdown("**Villes météo affichées**")
        st.caption("🟡🟠🔴 Couleur des points = température moyenne (°C)")
        villes_map_sel = st.multiselect("Villes sur la carte", VILLES_ORDRE, default=VILLES_ORDRE)

    with col2:
        forets_f = forets[forets["region"].isin(regions_sel)]
        fig_map = go.Figure()

        # Couche 1 : polygones des forêts, une trace par région pour une légende lisible
        for region in sorted(forets_f["region"].unique()):
            feats = [f for f in forets_geojson["features"] if f["properties"]["region"] == region]
            if not feats:
                continue
            geojson_r = {"type": "FeatureCollection", "features": feats}
            noms = [f["properties"]["nom"] for f in feats]
            fig_map.add_trace(go.Choroplethmap(
                geojson=geojson_r,
                locations=noms,
                z=[1] * len(noms),
                featureidkey="properties.nom",
                colorscale=[[0, REGION_COLORS.get(region, "#999999")], [1, REGION_COLORS.get(region, "#999999")]],
                showscale=False,
                marker_opacity=0.55,
                marker_line_width=1,
                marker_line_color="rgba(0,0,0,0.35)",
                text=noms,
                hovertemplate="%{text}<br>Région: " + region + "<extra></extra>",
                name=region,
                showlegend=True,
            ))

        # Couche 2 : villes météo superposées, taille/couleur = température moyenne max
        avg_temp_map = temp[temp["type_temp"] == "Températures maximales"].groupby("ville", observed=True)["value"].mean()
        villes_plot = [v for v in villes_map_sel if v in VILLE_COORDS]
        lats = [VILLE_COORDS[v][0] for v in villes_plot]
        lons = [VILLE_COORDS[v][1] for v in villes_plot]
        temps_plot = [avg_temp_map.get(v, None) for v in villes_plot]

        fig_map.add_trace(go.Scattermap(
            lat=lats, lon=lons, mode="markers+text",
            marker=dict(
                size=22, color=temps_plot, colorscale="YlOrRd",
                cmin=min(avg_temp_map), cmax=max(avg_temp_map),
                showscale=True, colorbar=dict(title="T° max<br>moy. (°C)", x=1.0),
                opacity=0.95,
            ),
            text=villes_plot,
            textposition="top center",
            textfont=dict(size=11, color="#1f2937"),
            hovertext=[f"{v}<br>T° max moy. : {t:.1f}°C" for v, t in zip(villes_plot, temps_plot)],
            hovertemplate="%{hovertext}<extra></extra>",
            name="Villes (température)",
            showlegend=True,
        ))

        fig_map.update_layout(
            map_style="carto-positron",
            map_zoom=6.0,
            map_center={"lat": 8.6, "lon": 0.95},
            height=580,
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", y=-0.02, bgcolor="rgba(255,255,255,0.85)"),
        )
        st.plotly_chart(fig_map, use_container_width=True)
    analysis_caption(
        "<b>Lecture :</b> chaque couleur de polygone correspond à une région administrative (voir légende à "
        "gauche), les points colorés sont les 10 villes météo — plus le point est rouge/foncé, plus la "
        "température maximale moyenne y est élevée. On observe que les points les plus chauds (Nord) se "
        "trouvent dans les zones où les polygones forestiers sont les plus rares."
    )

    st.markdown("**Détail des forêts classées**")
    forets_display = forets_f[["nom", "region", "prefecture", "commune", "creation"]].rename(
        columns={"nom": "Nom", "region": "Région", "prefecture": "Préfecture",
                 "commune": "Commune", "creation": "Année de création"}
    )
    st.dataframe(forets_display, use_container_width=True, hide_index=True)

# ================= ONGLET 6 : RECOMMANDATIONS =================
with tabs[5]:
    section_tag("Objectif 6 — recommandations stratégiques")
    st.subheader("De l'état des lieux à l'action : quatre leviers à activer ensemble")

    constat_box(
        "🧭 Synthèse de l'état des lieux",
        "Trois fractures se superposent sur les mêmes territoires, principalement au Nord et dans les zones "
        "rurales des Plateaux et des Savanes : un accès à l'électricité très inégal (écart ville-village de "
        "plusieurs dizaines de points), une dépendance quasi totale au bois-énergie pour la cuisson, et une "
        "couverture en forêts classées plus faible là où le climat est le plus rude. Les recommandations "
        "ci-dessous s'attaquent aux trois à la fois, plutôt qu'à chacune isolément.",
        kind="neutral"
    )

    st.write("")
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(f"""
        <div class="reco-card" style="--r-accent:{TOGO_GREEN};">
        <div class="reco-title">☀️ Électrifier les villages</div>
        <ul>
        <li>Kits solaires individuels et mini-réseaux villageois dans les zones rurales isolées</li>
        <li>Prioriser Savanes et Kara, où l'accès rural est le plus faible et le climat le plus rude</li>
        <li>Réduire délais et coûts de raccordement pour lever un frein direct à l'adoption</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div class="reco-card" style="--r-accent:{TOGO_YELLOW};">
        <div class="reco-title">🔥 Cuisson propre</div>
        <ul>
        <li>Subventionner les foyers améliorés à bois/charbon (-30 à -50% de bois consommé)</li>
        <li>Développer la filière gaz butane (LPG) en zone rurale, aujourd'hui quasi absente</li>
        <li>Cibler en priorité les zones à forte dépendance au bois-énergie du Nord</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    with r3:
        st.markdown(f"""
        <div class="reco-card" style="--r-accent:{TOGO_RED};">
        <div class="reco-title">🌳 Protéger les forêts</div>
        <ul>
        <li>Renforcer surveillance et reboisement dans Plateaux et Savanes, les plus exposées</li>
        <li>Étendre le réseau de forêts classées en Savanes, région la moins couverte</li>
        <li>Lier les projets d'électrification rurale à des clauses de réduction de la coupe de bois</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    with r4:
        st.markdown(f"""
        <div class="reco-card" style="--r-accent:#0072B2;">
        <div class="reco-title">📣 Sensibiliser les citoyens</div>
        <ul>
        <li>Campagnes locales (radios communautaires, chefs de village) sur les foyers améliorés</li>
        <li>Programmes scolaires sur le lien entre bois-énergie et recul des forêts</li>
        <li>Valoriser les villages pilotes solaires comme modèles reproductibles pour leurs voisins</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    constat_box(
        "🔗 Constat clé reliant les quatre axes",
        "Tant que l'électricité n'atteint pas les villages, les ménages restent dépendants du bois pour cuisiner "
        "— ce qui alimente la déforestation, laquelle aggrave à son tour la hausse locale des températures "
        "observée notamment au Nord. Électrification rurale, cuisson propre, protection forestière et "
        "sensibilisation citoyenne doivent donc être conduites comme <b>un seul programme intégré</b>, et non "
        "quatre politiques séparées.",
        kind="positif"
    )
