import unicodedata
import re
from dolores_keywords import dolores


# 🔄 Diccionario de sinónimos (clave → lista de sinónimos que se normalizan a esa clave)
sinonimos = {
    "facturacion": ["factura", "boleta", "cobro"],
    "precio":      ["valor", "costo"],
    "servicio":    ["atencion", "soporte", "ayuda"],
    "tecnico":     ["tecnica", "tecnologia"],
    "pago":        ["abono", "deposito"],
    "cliente":     ["usuario", "abonado"]
}

# 🧹 Conectores (stopwords) que se eliminarán al normalizar el texto
conectores = {
    "que", "y", "pero", "porque", "por", "para", "con",
    "sin", "de", "la", "el", "en", "lo", "a", "un", "una",
    "al", "del"
    # Puedes agregar aquí cualquier palabra adicional que consideres “conector”
}


def normalizar_texto(texto):
    """
    1) Pasa a minúsculas
    2) Quita tildes/acentos (texto ASCII básico)
    3) Elimina signos de puntuación (reemplazándolos por espacio)
    4) Divide en tokens y elimina las palabras que estén en 'conectores'
    5) Devuelve la frase “limpia” unida por espacios
    """
    if not isinstance(texto, str):
        return ""

    # Pasar a minúsculas
    texto = texto.lower()
    # Quitar acentos/tildes
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    # Reemplazar todo lo que no sea letra o dígito por espacio
    texto = re.sub(r"[^\w\s]", " ", texto)
    # Separar en tokens y filtrar conectores
    tokens = [tok for tok in texto.split() if tok not in conectores]
    # Reconstruir frase limpia
    return " ".join(tokens)


def expandir_sinonimos(frase):
    """
    Reemplaza en la frase normalizada cada sinónimo por su clave.
    Ejemplo: “cobro” → “facturacion”, “valor” → “precio”, etc.
    """
    for clave, lista_sins in sinonimos.items():
        for sin in lista_sins:
            # Buscamos coincidencia de palabra completa (\b...\b)
            frase = re.sub(rf"\b{re.escape(sin)}\b", clave, frase)
    return frase


def contiene_clave_flexible(frase_cliente, clave_normalizada):
    """
    - Si la clave contiene más de una palabra, chequea que todas estén presentes en 'frase_cliente' (sin importar orden).
    - Si es una sola palabra, hace búsqueda con límites de palabra (\b...\b) para no matchear substrings parciales.
    """
    if " " in clave_normalizada:
        # clave con varias palabras: chequeamos que cada token aparezca en frase_cliente
        tokens = clave_normalizada.split()
        return all(tok in frase_cliente for tok in tokens)
    else:
        # clave de una sola palabra: usamos word-boundaries
        return bool(re.search(rf"\b{re.escape(clave_normalizada)}\b", frase_cliente))


def detectar_dolor(verbatim):
    """
    1) Validación inicial: retorna Sin Dolor Detectado si no hay texto relevante.
    2) Normaliza y expande sinónimos.
    3) Recorre cada categoría en 'dolores' (salta "Indefinido" y "Vacío").
    4) Por cada frase clave, si hay match flexible, devuelve la categoría.
    5) Finalmente, si nada encaja, retorna "Sin Dolor Detectado".
    """
    # 1) Verificar tipo y contenido básico
    if not isinstance(verbatim, str) or not verbatim.strip():
        return "Sin Dolor Detectado"
    # Exigir al menos 3 letras consecutivas (evita cadenas no relevantes)
    if not re.search(r"\b[a-zA-Z]{3,}\b", verbatim):
        return "Sin Dolor Detectado"

    # 2) Normalizar y expandir sinónimos
    verbatim_norm = normalizar_texto(verbatim)
    verbatim_norm = expandir_sinonimos(verbatim_norm)

    # 3) Recorrer categorías principales
    for categoria, lista_frases in dolores.items():
        if categoria in ["Indefinido", "Vacío"]:
            continue
        for frase_clave in lista_frases:
            clave_norm = normalizar_texto(frase_clave)
            if clave_norm and contiene_clave_flexible(verbatim_norm, clave_norm):
                return categoria

    # 4) Ninguna coincidencia: fallback
    return "Sin Dolor Detectado"
