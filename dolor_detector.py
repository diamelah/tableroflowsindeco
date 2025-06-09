import re
import unicodedata
from dolores_keywords import dolores
import pandas as pd

def normalizar_texto(texto):
    texto = str(texto).lower()
    # Saca tildes/acentos
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = re.sub(r'[^\w\s]', '', texto)  # Saca signos y puntuación
    return texto.strip()

def es_comentario_vacio(texto):
    texto = normalizar_texto(texto)
    return texto == "" or texto in ["nan", "none", ".", "..", "...", ".....", "sin palabras"]

def detectar_dolor(verbatim):
    verbatim = normalizar_texto(verbatim)
    if es_comentario_vacio(verbatim):
        return "Vacío"
    dolores_detectados = []
    for categoria, frases in dolores.items():
        if categoria in ["Indefinido", "Vacío"]:
            continue
        for frase in frases:
            if normalizar_texto(frase) in verbatim:
                dolores_detectados.append(categoria)
                break
    return ", ".join(dolores_detectados) if dolores_detectados else "Sin Dolor Detectado"

def clasificar_dolores(df):
    # No invento nada, solo tu lógica original
    from utils import detectar_dolor
    if 'verbatim' in df.columns:
        df['Dolor'] = df['verbatim'].apply(detectar_dolor)
    elif '2 - ¿Cuál es el motivo de tu calificación?' in df.columns:
        df['Dolor'] = df['2 - ¿Cuál es el motivo de tu calificación?'].apply(detectar_dolor)
    else:
        raise ValueError("No se encuentra la columna de comentarios (verbatim) en el dataframe.")
    return df

def filtrar_alerta_match(df):
    def match_alerta(dolores):
        if pd.isna(dolores):
            return "No"
        if "Alerta Match" in dolores:
            return "Sí"
        return "No"
    if "Dolor" in df.columns:
        df["Maltrato Detectado"] = df["Dolor"].apply(match_alerta)
    else:
        df["Maltrato Detectado"] = "No"
    return df
