# filtros_sidebar.py mejorado
import streamlit as st
import pandas as pd

def aplicar_filtros(df):
    st.sidebar.subheader("👩‍💻​ Filtros")

    # Filtro por fecha
    if "Fecha" in df.columns:
        fechas = pd.to_datetime(df["Fecha"], errors='coerce')
        fecha_min, fecha_max = fechas.min(), fechas.max()
        rango_fechas = st.sidebar.date_input("Seleccioná un rango de fechas:", [fecha_min, fecha_max], min_value=fecha_min, max_value=fecha_max)
        df = df[(fechas >= pd.to_datetime(rango_fechas[0])) & (fechas <= pd.to_datetime(rango_fechas[1]))]

    # Filtro por Grupo NPS
    if "Grupo NPS" in df.columns:
        grupo_nps_opciones = df["Grupo NPS"].dropna().unique().tolist()
        grupo_nps = st.sidebar.multiselect(
            "👥 Grupo NPS",
            options=["Todos"] + grupo_nps_opciones,
            default=["Todos"]
        )
        if "Todos" not in grupo_nps:
            df = df[df["Grupo NPS"].isin(grupo_nps)]

    # Filtro por Dolor
    if "Dolor" in df.columns:
        # Asegurarse de que todo sea string separado por comas
        df["Dolor"] = df["Dolor"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

        lista_dolores = sorted(set([
            d.strip() for sublist in df["Dolor"].dropna().str.split(",")
            for d in sublist
        ]))
        lista_dolores = [d for d in lista_dolores if d not in ["Indefinido", "Vacío", ""]]

        dolores_seleccionados = st.sidebar.multiselect(
            "💥 Tipo de Dolor",
            options=["Todos"] + lista_dolores,
            default=["Todos"]
        )

        if "Todos" not in dolores_seleccionados:
            df = df[df["Dolor"].str.contains("|".join(dolores_seleccionados), na=False)]


    # Filtro por causa (Q2.1)
    causa_col = "¿Cuál fue el factor que más influyó en tu nota?"
    if causa_col in df.columns:
        causas_unicas = df[causa_col].dropna().unique()
        causa_seleccionada = st.sidebar.multiselect(
            "📌 ¿Cuál fue el factor que más influyó en tu nota?",
            options=["Todas"] + sorted(causas_unicas),
            default=["Todas"]
        )
        if "Todas" not in causa_seleccionada:
            df = df[df[causa_col].isin(causa_seleccionada)]
            
    # Filtro ¿Qué tan fácil te resulta usar Flow? Q3.1
    causa_col = "¿Qué tan fácil te resulta usar Flow? Q3.1"
    if causa_col in df.columns:
        causas_unicas = df[causa_col].dropna().unique()
        causa_seleccionada = st.sidebar.multiselect(
            "¿Qué tan fácil te resulta usar Flow? Q3.1",
            options=["Todas"] + sorted(causas_unicas),
            default=["Todas"]
        )
        if "Todas" not in causa_seleccionada:
            df = df[df[causa_col].isin(causa_seleccionada)]
            
    # Filtro Q5.1 En el último mes, ¿Te contactaste con nuestro centro de atención al cliente 
    # (Canal digital, telefónico y/o presencial)?
    causa_col = "¿Te contactaste con nuestro centro de atención? Q5.1"
    if causa_col in df.columns:
        causas_unicas = df[causa_col].dropna().unique()
        causa_seleccionada = st.sidebar.multiselect(
            "¿Te contactaste con nuestro centro de atención? Q5.1",
            options=["Todas"] + sorted(causas_unicas),
            default=["Todas"]
        )
        if "Todas" not in causa_seleccionada:
            df = df[df[causa_col].isin(causa_seleccionada)]
            
    # Filtro Q5.2 ¿A través de que canal/es te contactaste?
    causa_col = "¿A través de que canal/es te contactaste? Q5.2"
    if causa_col in df.columns:
        causas_unicas = df[causa_col].dropna().unique()
        causa_seleccionada = st.sidebar.multiselect(
            "¿A través de que canal/es te contactaste? Q5.2",
            options=["Todas"] + sorted(causas_unicas),
            default=["Todas"]
        )
        if "Todas" not in causa_seleccionada:
            df = df[df[causa_col].isin(causa_seleccionada)]
            
    # Filtro Q5.3 ¿Fue resuelto el motivo de tu contacto?
    causa_col = "¿Fue resuelto el motivo de tu contacto? Q5.3"
    if causa_col in df.columns:
        causas_unicas = df[causa_col].dropna().unique()
        causa_seleccionada = st.sidebar.multiselect(
            "¿Fue resuelto el motivo de tu contacto? Q5.3",
            options=["Todas"] + sorted(causas_unicas),
            default=["Todas"]
        )
        if "Todas" not in causa_seleccionada:
            df = df[df[causa_col].isin(causa_seleccionada)]
            
    # Filtro TECNOLOGIA
    causa_col = "TECNOLOGIA_FLOW"
    if causa_col in df.columns:
        causas_unicas = df[causa_col].dropna().unique()
        causa_seleccionada = st.sidebar.multiselect(
            "TECNOLOGIA_FLOW",
            options=["Todas"] + sorted(causas_unicas),
            default=["Todas"]
        )
        if "Todas" not in causa_seleccionada:
            df = df[df[causa_col].isin(causa_seleccionada)]
    

    return df.reset_index(drop=True)
