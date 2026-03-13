import os
import json
import csv
import feedparser
import requests
import random
from datetime import datetime

# --- CONFIGURACIÓN ---

def limpiar_resumen(texto):
    # Limpia el HTML que a veces trae el RSS de Google
    if not texto:
        return "Sin descripción disponible."
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
            
            # Aplicamos aleatoriedad sobre los 3 primeros resultados para variar el historial
            if len(feed.entries) > 0:
                limite = min(len(feed.entries), 3)
                entry = random.choice(feed.entries[:limite])
                
                resumen_sucio = entry.summary if 'summary' in entry else entry.title
                resumen_ia = limpiar_resumen(resumen_sucio)
                
                noticias[cat] = {
                    "titulo": entry.title,
                    "resumen": resumen_ia[:150] + "...",
                    "url": entry.link
                }
            else:
                raise Exception("No hay entradas")
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

    # 1. Guardar para la WEB (noticias.json)
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)

    # 2. Guardar en el histórico (historico_noticias.csv)
    archivo_historial = 'historico_noticias.csv'
    existe = os.path.isfile(archivo_historial)
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Fecha', 'Categoria', 'Titulo', 'URL', 'Resumen'])
        for cat, data in noticias.items():
            writer.writerow([hoy, cat.upper(), data['titulo'], data['url'], data['resumen']])
    
    print(f"✅ Proceso finalizado. Historial actualizado a las {hoy}")

if __name__ == "__main__":
    ejecutar_flujo()
