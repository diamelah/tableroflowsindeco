import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from streamlit_echarts import st_echarts

def cargar_datos(excel_file):
    try:
        df = pd.read_excel(excel_file, sheet_name=None, header=0)  # encabezado en la fila 1

        for nombre_hoja, hoja in df.items():
            hoja = hoja.copy()
            hoja.columns = hoja.columns.str.strip()

            if "¿Cuál es el motivo de tu calificación?" in hoja.columns or "Q1.3" in hoja.columns:
                hoja.rename(columns={
                    "EndDate": "Fecha",
                    "Q1.1_NPS_GROUP": "Grupo NPS",
                    "dni": "DNI",
                    "Q1.3": "¿Cuál es el motivo de tu calificación?",
                    "Q2.1": "¿Cuál fue el factor que más influyó en tu nota?",
                    "Q2.2": "¿Cuál de estas opciones influyó más en tu elección?",
                    "Q3.1": "¿Qué tan fácil te resulta usar Flow? Q3.1",
                    "Q3.2": "¿Nos contarías por qué motivo te resultó difícil? Q3.2",
                    "Q3.5": "¿Cómo calificas la relación entre lo que pagas y el servicio que te brindamos?",
                    "Q4.3": "¿Tuviste inconveniente con el servicio?",
                    "Q5.1": "¿Te contactaste con nuestro centro de atención? Q5.1",
                    "Q5.2": "¿A través de que canal/es te contactaste? Q5.2",
                    "Q5.3": "¿Fue resuelto el motivo de tu contacto? Q5.3",
                    "TECNOLOGIA_FLOW": "Tecnlogía"
                }, inplace=True)

                # Filtrar encabezados repetidos
                hoja = hoja[hoja["Fecha"] != "Fecha de finalización"]

                hoja.dropna(subset=["¿Cuál es el motivo de tu calificación?"], inplace=True)
                hoja["verbatim"] = hoja["¿Cuál es el motivo de tu calificación?"]

                
                # Marcar textos vacíos o con solo símbolos como indefinidos
                hoja = marcar_indefinidos(hoja, [
                    "¿Cuál es el motivo de tu calificación?",
                    "¿Nos contarías por qué motivo te resultó difícil? Q3.2"
                ])

                return hoja

        return None
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        return None


import re

def marcar_indefinidos(df, columnas_texto):
    """
    Marca como 'Indefinido' los registros que no contienen texto alfanumérico.
    Crea una nueva columna booleana por cada texto: <col>_es_indefinido
    """
    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
            df[col + "_es_indefinido"] = df[col].apply(lambda x: not re.search(r"\w", x))
    return df
