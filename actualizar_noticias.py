import feedparser
import json
import os
import csv
import random
from datetime import datetime

# --- CONFIGURACIÓN ---
CATEGORIAS = {
    "FAMILIA": "https://news.google.com/rss/search?q=sentencia+OR+reforma+derecho+familia+España+OR+custodia+compartida+when:48h&hl=es&gl=ES&ceid=ES:es",
    "PENAL": "https://news.google.com/rss/search?q=sentencia+OR+tribunal+derecho+penal+España+-opinión+-tribuna+-política+when:24h&hl=es&gl=ES&ceid=ES:es",
    "MERCANTIL": "https://news.google.com/rss/search?q=concurso+acreedores+España+noticias+mercantil+when:24h&hl=es&gl=ES&ceid=ES:es",
    "EXTRANJERIA": "https://news.google.com/rss/search?q=reforma+reglamento+extranjería+España+OR+BOE+when:24h&hl=es&gl=ES&ceid=ES:es"
}

HISTORICO_FILE = 'historico_noticias.csv'
JSON_FILE = 'noticias.json'
LOG_LINKEDIN = 'log_linkedin.txt'
POST_LINKEDIN_FILE = 'ultimo_post_linkedin.txt'

def noticia_ya_publicada(url_nueva):
    if not os.path.exists(HISTORICO_FILE): return False
    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        return any(url_nueva in line for line in f)

def guardar_en_historico(categoria, titulo, url):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(HISTORICO_FILE, mode='a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([ahora, categoria, titulo, url])

def obtener_ultimas_del_historico():
    ultimas = {}
    if not os.path.exists(HISTORICO_FILE): return {}
    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        for fila in csv.reader(f):
            if len(fila) >= 4:
                ultimas[fila[1]] = {"titulo": fila[2], "url": fila[3], "fecha": fila[0]}
    return ultimas

def redactar_post_profesional(categoria, noticia):
    return (
        f"🚀 {noticia['titulo'].upper()}\n\n"
        f"⚖️ ACTUALIDAD JURÍDICA: {categoria.capitalize()}\n"
        f"Analizar la jurisprudencia reciente es vital para anticipar soluciones legales efectivas.\n\n"
        f"🔹 Claves de la reciente actualización del sector.\n"
        f"🔍 El conocimiento actualizado marca la diferencia.\n\n"
        f"👇 Noticia completa:\n{noticia['url']}\n\n"
        f"#Abogado #Derecho #{categoria.capitalize()}"
    )

def ejecutar_sincronizacion():
    for cat, url_rss in CATEGORIAS.items():
        feed = feedparser.parse(url_rss)
        for entrada in feed.entries:
            if not noticia_ya_publicada(entrada.link):
                guardar_en_historico(cat, entrada.title.split(' - ')[0].strip(), entrada.link)
                break

    datos = obtener_ultimas_del_historico()
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

    # Selección para LinkedIn
    candidatas = list(CATEGORIAS.keys())
    cat_elegida = random.choice(candidatas)
    if cat_elegida in datos:
        texto = redactar_post_profesional(cat_elegida, datos[cat_elegida])
        with open(POST_LINKEDIN_FILE, 'w', encoding='utf-8') as f:
            f.write(texto)

if __name__ == "__main__":
    ejecutar_sincronizacion()
