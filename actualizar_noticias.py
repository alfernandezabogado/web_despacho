import feedparser
import requests
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
    try:
        with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            return any(len(fila) > 3 and url_nueva == fila[3] for fila in reader)
    except: return False

def guardar_en_historico(categoria, titulo, url):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(HISTORICO_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([ahora, categoria, titulo, url])

def obtener_ultimas_del_historico():
    ultimas = {}
    for cat in CATEGORIAS.keys():
        ultimas[cat] = {"titulo": f"Actualidad en {cat.capitalize()}", "resumen": "", "url": "", "fecha": ""}
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for fila in reader:
                if len(fila) >= 4:
                    ultimas[fila[1]] = {"titulo": fila[2], "resumen": f"Novedades en {fila[1].lower()}.", "url": fila[3], "fecha": fila[0]}
    return ultimas

def redactar_post_profesional(categoria, noticia):
    """Genera el texto enriquecido para LinkedIn"""
    titulo = noticia['titulo'].upper()
    return (
        f"🚀 {titulo}\n\n"
        f"⚖️ ACTUALIDAD JURÍDICA: {categoria.capitalize()}\n"
        f"Analizar la jurisprudencia reciente es vital para anticipar soluciones legales. "
        f"Hoy destacamos esta novedad en {categoria.lower()}:\n\n"
        f"🔹 Impacto en procedimientos legales.\n"
        f"🔹 Claves de la actualización del sector.\n\n"
        f"👇 Consulta la noticia completa aquí:\n{noticia['url']}\n\n"
        f"#Abogado #Derecho #ActualidadJuridica #AngelLuisFernandez"
    )

def registrar_publicacion_linkedin(categoria, texto_post):
    """Guarda el log y CREA EL ARCHIVO DE TEXTO para el YAML"""
    with open(LOG_LINKEDIN, 'w') as f:
        f.write(categoria)
    with open(POST_LINKEDIN_FILE, 'w', encoding='utf-8') as f:
        f.write(texto_post)

def elegir_noticia_para_linkedin(datos_finales):
    ultima_cat = ""
    if os.path.exists(LOG_LINKEDIN):
        with open(LOG_LINKEDIN, 'r') as f: ultima_cat = f.read().strip()
    candidatas = [cat for cat in CATEGORIAS.keys() if datos_finales[cat]["url"] != "" and cat != ultima_cat]
    if not candidatas: candidatas = [cat for cat in CATEGORIAS.keys() if datos_finales[cat]["url"] != ""]
    if not candidatas: return None, None
    cat = random.choice(candidatas)
    return cat, datos_finales[cat]

def ejecutar_sincronizacion():
    # 1. RASTREO
    for cat, url_rss in CATEGORIAS.items():
        feed = feedparser.parse(url_rss)
        for entrada in feed.entries:
            if not noticia_ya_publicada(entrada.link):
                guardar_en_historico(cat, entrada.title.split(' - ')[0].strip(), entrada.link)
                break

    # 2. JSON WEB
    datos = obtener_ultimas_del_historico()
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

    # 3. LINKEDIN (LA PARTE CRÍTICA)
    cat_link, noticia_link = elegir_noticia_para_linkedin(datos)
    if cat_link:
        texto = redactar_post_profesional(cat_link, noticia_link)
        registrar_publicacion_linkedin(cat_link, texto) # Crea el archivo que el YAML necesita
        print(f"✅ Post preparado para LinkedIn: {cat_link}")

if __name__ == "__main__":
    ejecutar_sincronizacion()
