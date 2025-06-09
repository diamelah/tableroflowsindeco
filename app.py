import streamlit as st
import pandas as pd
from data_loader import cargar_datos
from dolor_detector import clasificar_dolores, filtrar_alerta_match
from visualizaciones import mostrar_nps_general, mostrar_tabla_general, mostrar_contacto_y_resolucion, mostrar_precio_promociones
from filtros_sidebar import aplicar_filtros
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Dash FLOW S/DECO", layout="wide")
st.title("📊 Dashboard FLOW S/DECO")

# Subida del archivo Excel
uploaded_file = st.sidebar.file_uploader("📁 Subí tu archivo Excel", type=["xlsx"])

if uploaded_file:
    df = cargar_datos(uploaded_file)

    if df is not None and not df.empty:
        # Guardar el DataFrame original sin filtrar
        df_original = df.copy()

        # Clasificación de dolores y maltrato solo una vez
        df = clasificar_dolores(df)
        df = filtrar_alerta_match(df)

        # Aplicar filtros luego del análisis
        df_filtrado = aplicar_filtros(df)

        # Recuperar la selección de Grupo NPS hecha en aplicar_filtros (usando session_state)
        seleccion_grupo = st.session_state.get("seleccion_grupo", "Todos")

        tab1, tab2, tab3 = st.tabs([
            "📊​ NPS General",
            "📋 Análisis de Verbatims",
            "🎯​ Precio y Promociones",
            
        ])

        with tab1:
            mostrar_nps_general(df_filtrado)

        with tab2:
            mostrar_tabla_general(df_filtrado)
            mostrar_contacto_y_resolucion(df_filtrado)

        with tab3:
            mostrar_precio_promociones(df_filtrado, df_original, seleccion_grupo)

        
else:
    st.info("📄 Esperando que subas un archivo Excel para comenzar.")
