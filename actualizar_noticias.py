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
LOG_LINKEDIN = 'log_linkedin.txt' # Archivo para recordar la última publicación

# --- 1. FUNCIONES DE APOYO Y DATOS ---

def noticia_ya_publicada(url_nueva):
    if not os.path.exists(HISTORICO_FILE): return False
    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return any(len(fila) > 3 and url_nueva == fila[3] for fila in reader)

def guardar_en_historico(categoria, titulo, url):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(HISTORICO_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([ahora, categoria, titulo, url])

def obtener_ultimas_del_historico():
    ultimas = {}
    if not os.path.exists(HISTORICO_FILE): return ultimas
    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for fila in reader:
            if len(fila) >= 4:
                fecha_str, cat, titulo, url = fila[0], fila[1], fila[2], fila[3]
                ultimas[cat] = {
                    "titulo": titulo.split(' - ')[0],
                    "resumen": f"Últimas novedades legislativas en {cat.capitalize()}.",
                    "url": url,
                    "fecha": fecha_str
                }
    return ultimas

# --- 2. LÓGICA DE INTELIGENCIA PARA LINKEDIN ---

def obtener_ultima_categoria_linkedin():
    """Lee qué categoría se publicó la última vez."""
    if os.path.exists(LOG_LINKEDIN):
        with open(LOG_LINKEDIN, 'r') as f:
            return f.read().strip()
    return None

def registrar_publicacion_linkedin(categoria):
    """Guarda la categoría recién publicada."""
    with open(LOG_LINKEDIN, 'w') as f:
        f.write(categoria)

def elegir_noticia_para_linkedin(datos_finales):
    """Elige una noticia que NO sea de la misma categoría que la anterior."""
    ultima_cat = obtener_ultima_categoria_linkedin()
    # Filtramos las categorías disponibles quitando la última publicada
    candidatas = [cat for cat in datos_finales if cat != ultima_cat and cat != "fecha_sistema"]
    
    if not candidatas: # Si solo hay una categoría disponible, la usamos
        candidatas = [cat for cat in datos_finales if cat != "fecha_sistema"]
    
    cat_elegida = random.choice(candidatas)
    return cat_elegida, datos_finales[cat_elegida]

# --- 3. LÓGICA DE EJECUCIÓN ---

def buscar_nuevas_noticias():
    for cat, url_rss in CATEGORIAS.items():
        feed = feedparser.parse(url_rss)
        for entrada in feed.entries:
            if not noticia_ya_publicada(entrada.link):
                titulo_limpio = entrada.title.split(' - ')[0]
                guardar_en_historico(cat, titulo_limpio, entrada.link)
                break

def ejecutar_sincronizacion():
    print("🤖 Sincronizando e iniciando selección para LinkedIn...")
    buscar_nuevas_noticias()
    datos_finales = obtener_ultimas_del_historico()
    
    if datos_finales:
        datos_finales["fecha_sistema"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, ensure_ascii=False, indent=4)
        
        # SELECCIÓN INTELIGENTE PARA LINKEDIN
        cat, noticia = elegir_noticia_para_linkedin(datos_finales)
        print(f"🎯 Seleccionada noticia de {cat} para LinkedIn (evitando repetir {obtener_ultima_categoria_linkedin()})")
        
        # Aquí llamarías a tu función de publicar_en_linkedin(noticia)
        # Y si tiene éxito:
        registrar_publicacion_linkedin(cat)
        
        print(f"✅ Proceso completado.")

if __name__ == "__main__":
    ejecutar_sincronizacion()
