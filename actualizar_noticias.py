import random # Añadimos esto arriba

def buscar_datos_ia():
    # ... (tu código anterior) ...
    
    for cat, busqueda in conceptos.items():
        try:
            url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es&gl=ES&ceid=ES:es"
            feed = feedparser.parse(url_rss)
            
            if len(feed.entries) > 1:
                # En lugar de coger siempre la 0 (la primera), 
                # cogemos una al azar de entre las 3 primeras.
                entry = random.choice(feed.entries[:3]) 
                
                noticias[cat] = {
                    "titulo": entry.title,
                    "resumen": limpiar_resumen(entry.summary)[:150] + "...",
                    "url": entry.link
                }
    # ... (resto del código) ...
import os
import json
import csv
import feedparser
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
# Si quieres usar IA de verdad, necesitarías una API KEY de Hugging Face (gratis)
# Por ahora lo haremos con lógica de "Smart Extraction" para que no falle en GitHub
def limpiar_resumen(texto):
    # Limpia el HTML que a veces trae el RSS de Google
    if "<" in texto:
        return texto.split('<')[0]
    return texto

def buscar_datos_ia():
    conceptos = {
        "familia": "sentencia+custodia+compartida+España",
        "penal": "Tribunal+Supremo+penal+España",
        "mercantil": "BOE+resolucion+concursal",
        "extranjeria": "reforma+reglamento+extranjeria+España"
    }
    
    noticias = {}
    
    for cat, busqueda in conceptos.items():
        try:
            url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es&gl=ES&ceid=ES:es"
            feed = feedparser.parse(url_rss)
            
            if feed.entries:
                entry = feed.entries[0]
                # Aquí simulamos el "summarizer" extrayendo la parte mollar
                resumen_ia = limpiar_resumen(entry.summary if 'summary' in entry else entry.title)
                
                noticias[cat] = {
                    "titulo": entry.title,
                    "resumen": resumen_ia[:150] + "...", # El resumen para la web
                    "url": entry.link
                }
        except Exception as e:
            noticias[cat] = {
                "titulo": f"Actualidad {cat.capitalize()}",
                "resumen": "Consulta las últimas novedades del sector en el enlace.",
                "url": "https://noticias.juridicas.com"
            }
    return noticias

def ejecutar_flujo():
    noticias = buscar_datos_ia()
    hoy = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 1. Guardar para la WEB (con el nuevo campo 'resumen')
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)

    # 2. Guardar en tu HDD de 1 TB (CSV)
    archivo_historial = 'historico_noticias.csv'
    existe = os.path.isfile(archivo_historial)
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Fecha', 'Categoria', 'Titulo', 'URL', 'Resumen'])
        for cat, data in noticias.items():
            writer.writerow([hoy, cat.upper(), data['titulo'], data['url'], data['resumen']])

if __name__ == "__main__":
    ejecutar_flujo()
