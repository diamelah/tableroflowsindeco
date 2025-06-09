import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from streamlit_echarts import st_echarts
from utils import normalizar_texto
from utils import detectar_dolor

try:
    from streamlit_echarts import st_echarts
except ImportError:
    st.warning("❌ No se pudo cargar 'streamlit_echarts'. Instalalo con: pip install streamlit-echarts")
    st_echarts = None

# --- Mostrar NPS General ---
def mostrar_nps_general(df):
    if df.empty:
        st.warning("⚠️ No hay datos para mostrar con los filtros actuales.")
        return
    st.subheader("📊 Indicadores Generales de la Encuesta")

    df.columns = df.columns.str.strip()

    col_fecha = "Fecha"
    col_nps_group = "Grupo NPS"
    col_dni = "DNI"
    col_q13 = "¿Cuál es el motivo de tu calificación?"
    col_q21 = "¿Cuál fue el factor que más influyó en tu nota?"
    # Ajuste nombres de Q3
    col_q31 = "¿Qué tan fácil te resulta usar Flow? Q3.1"
    col_q32 = "¿Nos contarías por qué motivo te resultó difícil? Q3.2"

    columnas_necesarias = [col_fecha, col_nps_group, col_dni, col_q13, col_q21]
    faltantes = [col for col in columnas_necesarias if col not in df.columns]
    if faltantes:
        st.error(f"❌ Faltan columnas necesarias en el archivo: {faltantes}")
        return

    total_encuestas = df.shape[0]
    verbatims = df[col_q13].fillna("").apply(lambda x: x.strip()).apply(lambda x: x if x not in ["", "-", "--", "-"] else None).dropna().shape[0]
    vacios = total_encuestas - verbatims

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Q. Encuestas (total)", total_encuestas)
    with col2:
        st.metric("Q. Verbatims (con contenido)", verbatims)
    with col3:
        st.metric("Q. Verbatims Vacíos", vacios)

    st.divider()

    st.markdown("### 🧮 Distribución de Grupo NPS")
    nps_counts = df[col_nps_group].fillna("Vacío").value_counts(normalize=True).mul(100).round(2)

    prom = nps_counts.get("Promotor", 0.0)
    pas = nps_counts.get("Pasivo", 0.0)
    det = nps_counts.get("Detractor", 0.0)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style='background-color:#28a745;color:white;padding:10px;border-radius:10px;text-align:center;'>
            <h3 style='margin:0;'>😊 {prom}%</h3>
            <div style='font-size:18px;font-weight:bold;'>Promotores</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='background-color:#ffc107;padding:10px;border-radius:10px;text-align:center;'>
            <h3 style='margin:0;'>😐 {pas}%</h3>
            <div style='font-size:18px;font-weight:bold;'>Pasivos</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style='background-color:#dc3545;color:white;padding:10px;border-radius:10px;text-align:center;'>
            <h3 style='margin:0;'>😠 {det}%</h3>
            <div style='font-size:18px;font-weight:bold;'>Detractores</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### Q2.1 ¿Cuál fue el factor que más influyó en tu nota? por Grupo NPS")
    tabla_q21 = pd.crosstab(df[col_q21].fillna("Vacío"), df[col_nps_group].fillna("Vacío"))
    st.dataframe(tabla_q21)


# --- Tabla principal de verbatims ---
def mostrar_tabla_general(df):
    if df.empty:
        st.warning("⚠️ No hay datos para mostrar con los filtros actuales.")
        return

    st.subheader("📋 Tabla **¿Cuál es el motivo de tu calificación?**")
    st.subheader("🔍 Búsqueda personalizada")

    # Defino nombres de columnas para verbatim y Q3.2 y Q3.1
    col_q13 = "¿Cuál es el motivo de tu calificación?"
    col_q21 = "¿Cuál fue el factor que más influyó en tu nota?"
    col_q31 = "¿Qué tan fácil te resulta usar Flow? Q3.1"
    col_q32 = "¿Nos contarías por qué motivo te resultó difícil? Q3.2"

    # 1) Calcular columna 'Dolor' para el verbatim principal (Q1.3), si existe
    if col_q13 in df.columns:
        df["Dolor"] = df[col_q13].fillna("").astype(str).apply(detectar_dolor)
    else:
        df["Dolor"] = "Sin Dato"

    # 2) Lógica de búsqueda de palabras clave
    palabras_input = st.text_input("Buscar palabras clave (separadas por coma)", "")
    palabras = [normalizar_texto(p.strip()) for p in palabras_input.split(",") if p.strip()]

    df_filtrado = df.copy()
    if palabras:
        def contiene_palabras(texto):
            texto_norm = normalizar_texto(str(texto))
            return any(palabra in texto_norm for palabra in palabras)

        df_filtrado = df_filtrado[
            df_filtrado[col_q13].astype(str).apply(contiene_palabras)
        ]

    # 3) Construir lista de columnas a mostrar
    columnas_base = ["Fecha", "Grupo NPS", "DNI", col_q13, "Dolor"]
    if col_q21 in df_filtrado.columns:
        columnas_base.insert(-1, col_q21)

    # Checkbox para incluir todas las columnas al exportar
    incluir_todas = st.checkbox("Al exportar, incluir todas las columnas", value=False)

    # Si el usuario quiere todas las columnas, usamos df_filtrado completo; si no, solo columnas_base
    if incluir_todas:
        tabla_export = df_filtrado.copy()
    else:
        tabla_export = df_filtrado[columnas_base]

    # Mostrar la tabla en pantalla (solo columnas_base)
    st.dataframe(df_filtrado[columnas_base])

    # Botón de descarga: exporta según selección del checkbox
    output = BytesIO()
    tabla_export.to_excel(output, index=False, engine='openpyxl')
    st.download_button(
        label="📥 Descargar tabla de verbatims",
        data=output.getvalue(),
        file_name="tabla_verbaitms_general.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="descargar_verbaitms"
    )


    # ⬇️ Acá empieza la tabla adicional de Q3
    st.subheader("📋 Tabla **¿Qué tan fácil te resulta usar Flow?**")

    # 3) Calcular columna 'Dolor_Q3_2' para el campo Q3.2, si existe
    if col_q32 in df.columns:
        df["Dolor_Q3_2"] = df[col_q32].fillna("").astype(str).apply(detectar_dolor)
    else:
        df["Dolor_Q3_2"] = "Sin Dato"

    # 4) Defino las columnas a mostrar/descargar para Q3 (sólo Dolor_Q3_2 y Q3.1)
    columnas_q3 = [
        "Fecha",
        "Grupo NPS",
        "DNI",
        col_q31,
        col_q32,
        "Dolor_Q3_2"
    ]

    columnas_q3 = [col for col in columnas_q3 if col in df.columns]

    if columnas_q3:
        st.dataframe(df[columnas_q3])

        output_q3 = BytesIO()
        df[columnas_q3].to_excel(output_q3, index=False, engine='openpyxl')
        st.download_button(
            label="📥 Descargar tabla de facilidad de uso (Q3.1/Q3.2)",
            data=output_q3.getvalue(),
            file_name="tabla_facilidad_q3.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="descargar_facilidad_q3"
        )
        
        # 5) Tabla de doble entrada: Frecuencia de Q3.1 por mes
        if col_q31 in df.columns and "Fecha" in df.columns:
            df["Fecha_dt"] = pd.to_datetime(df["Fecha"], errors="coerce")
            df["Mes"] = df["Fecha_dt"].dt.strftime("%Y-%m")
            pivot_q31 = pd.crosstab(df[col_q31], df["Mes"])
            st.subheader("📊 Frecuencia de Q3.1 por Mes")
            st.dataframe(pivot_q31)

            output_pivot = BytesIO()
            pivot_q31.to_excel(output_pivot, engine='openpyxl')
            st.download_button(
                label="📥 Descargar tabla de Q3.1 por Mes",
                data=output_pivot.getvalue(),
                file_name="pivot_q3_1_por_mes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="descargar_pivot_q3_1"
            )
    else:
        st.info("ℹ️ Las columnas Q3.1, Q3.2 o Dolor_Q3_2 no están disponibles en este conjunto de datos.")


# --- Mostrar Contacto y Resolución (sustituido por doble entrada Q5.1) ---
def mostrar_contacto_y_resolucion(df):
    df.columns = df.columns.str.strip()
    st.markdown("### 📊 Frecuencia de Q5.1 por Mes (filtrada por Q5.2 y Q5.3)")

    # Columnas de interés
    col_q51 = "¿Te contactaste con nuestro centro de atención? Q5.1"
    col_q52 = "¿A través de que canal/es te contactaste? Q5.2"
    col_q53 = "¿Fue resuelto el motivo de tu contacto? Q5.3"

    # Verificar existencia de columnas necesarias
    if col_q51 not in df.columns or col_q53 not in df.columns or "Fecha" not in df.columns:
        st.warning("⚠️ No se encontraron las columnas necesarias (Q5.1, Q5.3 o Fecha) en los datos.")
        return

    # Convertir Fecha a datetime y extraer mes
    df["Fecha_dt"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Mes"] = df["Fecha_dt"].dt.to_period("M").astype(str)

    # Creamos dos columnas para alinear los radio buttons lado a lado
    col1, col2 = st.columns(2)

    # ----- FILTRO POR Q5.2 -----
    with col1:
        if col_q52 in df.columns:
            opciones_q52 = sorted(df[col_q52].dropna().unique().tolist())
            opciones_q52.insert(0, "Todos")
            opcion_canal = st.radio(
                "Filtrar por canal de contacto (Q5.2):",
                options=opciones_q52,
                key="radio_q52"
            )
        else:
            opcion_canal = "Todos"

    # ----- FILTRO POR Q5.3 -----
    with col2:
        opcion_resolucion = st.radio(
            "Filtrar por resolución del contacto (Q5.3):",
            options=["Todos", "Sí", "No", "Vacíos"],
            key="radio_q53"
        )

    # Filtrar datos según selecciones
    df_filtrado = df.copy()

    # Aplicar filtro Q5.2
    if col_q52 in df.columns and opcion_canal != "Todos":
        df_filtrado = df_filtrado[df_filtrado[col_q52] == opcion_canal]
    # Aplicar filtro Q5.3
    if opcion_resolucion == "Sí":
        df_filtrado = df_filtrado[df_filtrado[col_q53].astype(str).str.strip().str.lower() == "sí"]
    elif opcion_resolucion == "No":
        df_filtrado = df_filtrado[df_filtrado[col_q53].astype(str).str.strip().str.lower() == "no"]
    elif opcion_resolucion == "Vacíos":
        df_filtrado = df_filtrado[df_filtrado[col_q53].isna() | (df_filtrado[col_q53].astype(str).str.strip() == "")]
    
    # Crosstab: filas = categorías de Q5.1, columnas = Mes
    tabla_crosstab = pd.crosstab(
        df_filtrado[col_q51].fillna("Sin Respuesta"),
        df_filtrado["Mes"].fillna("Sin Fecha")
    )

    
    st.dataframe(tabla_crosstab)

    # Botón para descargar el crosstab como Excel
    output_ct = BytesIO()
    tabla_crosstab.to_excel(output_ct, index=True, engine='openpyxl')
    st.download_button(
        label="📥 Descargar tabla de Q5.1 por mes",
        data=output_ct.getvalue(),
        file_name="tabla_q51_por_mes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="descargar_q51_mes"
    )


    
# --- Mostrar precios y promociones (Q2.1, Q2.2, Q3.5) ---
def mostrar_precio_promociones(df_filtrado, df_original, seleccion_grupo):
    st.subheader("🎯​ Tabla de Precio y Promociones")
    
    columnas = list(dict.fromkeys([
        "Fecha",
        "DNI",
        "Grupo NPS",
        "¿Cuál fue el factor que más influyó en tu nota?",
        "¿Qué esperabas que incluyera esa nota?",
        "¿Cómo calificas la relación entre lo que pagas y el servicio que te brindamos?",
        "Dolor"
    ]))
    columnas_existentes = [col for col in columnas if col in df_filtrado.columns]
    if not columnas_existentes:
        st.warning("⚠️ Las columnas necesarias no están disponibles en este conjunto de datos.")
        return

    # Mostrar tabla basada en df_filtrado
    st.dataframe(df_filtrado[columnas_existentes])

    output = BytesIO()
    df_filtrado[columnas_existentes].to_excel(output, index=False, engine='openpyxl')
    st.download_button(
        label="📥 Descargar tabla de precio/promociones",
        data=output.getvalue(),
        file_name="tabla_precio_promociones.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="descargar_tabla_precio"
    )

    st.divider()
    # --- Gráfico de torta Q3.5 ---
    st.subheader("📊 Percepción Precio/Calidad")   
    col_q35 = "¿Cómo calificas la relación entre lo que pagas y el servicio que te brindamos?"

    # Determinar DataFrame para gráfico: todo si "Todos", sino filtrado
    if seleccion_grupo == "Todos":
        df_para_grafico = df_original.copy()
    else:
        df_para_grafico = df_filtrado.copy()

    if st_echarts and col_q35 in df_para_grafico.columns:
        conteo = (
            df_para_grafico[col_q35]
            .dropna()
            .astype(str)
            .str.strip()
            .loc[lambda x: ~x.isin(["", "-", "--", ".", "...", "NS/NC"]) ]
            .value_counts()
            .reset_index()
        )
        conteo.columns = ["name", "value"]
        data = conteo.to_dict(orient="records")

        if not data:
            st.info("ℹ️ No hay suficientes respuestas válidas en Q3.5 para mostrar el gráfico.")
        else:
            options = {
                "title": {
                    "text": " ",
                    "subtext": "Q3.5",
                    "left": "center"
                },
                "tooltip": {"trigger": "item"},
                "legend": {"orient": "vertical", "left": "left"},
                "series": [
                    {
                        "name": "Q3.5",
                        "type": "pie",
                        "radius": "50%",
                        "data": data,
                        "emphasis": {
                            "itemStyle": {
                                "shadowBlur": 10,
                                "shadowOffsetX": 0,
                                "shadowColor": "rgba(0, 0, 0, 0.5)",
                            }
                        },
                    }
                ],
            }
            st_echarts(options=options, height="500px")
    elif not st_echarts:
        st.info("ℹ️ ECharts no está disponible. Instalalo con: pip install streamlit-echarts")
    else:
        st.info("ℹ️ No se encontró la columna Q3.5 para graficar.")
