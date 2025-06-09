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
    texto = re.sub(r'[^\w\s]', ' ', texto)
    # Tokenizar
    palabras = texto.split()
    # Eliminar los conectores (stopwords)
    palabras_filtradas = [p for p in palabras if p not in conectores]
    return ' '.join(palabras_filtradas).strip()

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
    Devuelve la categoría de 'dolor' correspondiente al texto de entrada.
    - Si no es un string o está vacío (o solo tiene símbolos), devuelve "Sin Dolor Detectado".
    - Si no contiene al menos 3 letras seguidas, devuelve "Sin Dolor Detectado".
    - Luego normaliza y expande sinónimos.
    - Recorre todas las categorías de 'dolores' (excepto "Indefinido") y, para cada frase clave:
      - La normaliza con normalizar_texto().
      - Si no queda nada tras normalizar (""), la salta.
      - Aplica contiene_clave_flexible() para hacer matching.
      - Si encuentra coincidencia, devuelve la categoría correspondiente.
    - Si no encuentra nada, devuelve "Sin Dolor Detectado".
    """
    # 1) Si no es texto válido o está vacío (sin caracteres alfanuméricos)
    if not isinstance(verbatim, str) or not verbatim.strip():
        return "Sin Dolor Detectado"

    # 2) Si no hay al menos 3 letras consecutivas (para evitar que “...” o “123” matchee)
    if not re.search(r"\b[a-zA-Z]{3,}\b", verbatim):
        return "Sin Dolor Detectado"

    # 3) Normalizar y expandir sinónimos
    frase_cliente = normalizar_texto(verbatim)
    frase_cliente = expandir_sinonimos(frase_cliente)

    # 4) Recorrer cada categoría de 'dolores' (importado de dolores_keywords.py)
    for categoria, lista_frases in dolores.items():
        # Saltamos explícitamente la categoría "Indefinido"
        if categoria == "Indefinido":
            continue

        for frase_clave in lista_frases:
            # Normalizar la frase clave
            clave_norm = normalizar_texto(frase_clave)
            # Si la frase clave normalizada quedó vacía, saltamos
            if not clave_norm:
                continue

            # Si coincide (usando lógica flexible), devolvemos la categoría
            if contiene_clave_flexible(frase_cliente, clave_norm):
                return categoria

    # 5) Si no hubo coincidencias en ninguna categoría
    return "Sin Dolor Detectado"
