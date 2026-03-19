import feedparser
import requests
import json
import os
import csv
import random
from datetime import datetime

# --- CONFIGURACIÓN ---
CATEGORIAS = {
    "FAMILIA": "https://news.google.com/rss/search?q=sentencia+custodia+compartida+España+when:24h&hl=es&gl=ES&ceid=ES:es",
    "PENAL": "https://news.google.com/rss/search?q=derecho+penal+España+actualidad+when:24h&hl=es&gl=ES&ceid=ES:es",
    "MERCANTIL": "https://news.google.com/rss/search?q=concurso+acreedores+España+noticias+when:24h&hl=es&gl=ES&ceid=ES:es",
    "EXTRANJERIA": "https://news.google.com/rss/search?q=reforma+reglamento+extranjería+España+when:24h&hl=es&gl=ES&ceid=ES:es"
}

HISTORICO_FILE = 'historico_noticias.csv'
JSON_FILE = 'noticias.json'
LOG_LINKEDIN = 'log_linkedin.txt'

# --- 1. FUNCIONES DE APOYO Y DATOS ---

def noticia_ya_publicada(url_nueva):
    """Evita duplicados revisando el historial CSV."""
    if not os.path.exists(HISTORICO_FILE): return False
    try:
        with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            return any(len(fila) > 3 and url_nueva == fila[3] for fila in reader)
    except Exception:
        return False

def guardar_en_historico(categoria, titulo, url):
    """Guarda la noticia para que la web y el bot la recuerden."""
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    file_exists = os.path.isfile(HISTORICO_FILE)
    with open(HISTORICO_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([ahora, categoria, titulo, url])

def obtener_ultimas_del_historico():
    """Recupera la noticia más reciente de cada categoría para el JSON."""
    ultimas = {}
    # Inicialización por defecto para evitar campos vacíos en la web
    for cat in CATEGORIAS.keys():
        ultimas[cat] = {
            "titulo": f"Actualidad en {cat.capitalize()}",
            "resumen": f"Sincronizando las últimas novedades de {cat.lower()}...",
            "url": "",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    
    if not os.path.exists(HISTORICO_FILE): return ultimas

    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for fila in reader:
            if len(fila) >= 4:
                fecha_str, cat, titulo, url = fila[0], fila[1], fila[2], fila[3]
                if cat in ultimas:
                    ultimas[cat] = {
                        "titulo": titulo.strip(),
                        "resumen": f"Últimas novedades legislativas en {cat.capitalize()}.",
                        "url": url,
                        "fecha": fecha_str
                    }
    return ultimas

# --- 2. LÓGICA DE INTELIGENCIA PARA LINKEDIN ---

def obtener_ultima_categoria_linkedin():
    if os.path.exists(LOG_LINKEDIN):
        with open(LOG_LINKEDIN, 'r') as f:
            return f.read().strip()
    return None

def registrar_publicacion_linkedin(
