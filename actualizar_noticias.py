import os
import json
import csv
import feedparser
import requests
import random
from datetime import datetime

def es_dia_laborable():
    ahora = datetime.now()
    # 0=Lunes, 4=Viernes. 5 y 6 son Sábado y Domingo.
    if ahora.weekday() > 4:
        return False
    
    # Lista de festivos nacionales 2026 (puedes ampliarla)
    festivos_2026 = ["2026-01-01", "2026-01-06", "2026-04-03", "2026-05-01", "2026-10-12", "2026-12-25"]
    if ahora.strftime("%Y-%m-%d") in festivos_2026:
        return False
        
    return True

def publicar_en_linkedin(noticia):
    token = os.getenv('LINKEDIN_TOKEN')
    
    # Este pequeño bloque nos dirá quién eres
    url_id = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    
    res = requests.get(url_id, headers=headers)
    if res.status_code == 200:
        datos = res.json()
        print(f"🎯 TU MEMBER ID ES: urn:li:person:{datos['sub']}")
    else:
        print(f"❌ Error al obtener ID: {res.text}")
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
    # 1. Obtenemos las noticias frescas
    noticias = buscar_datos_ia()
    hoy_dt = datetime.now()
    hoy_str = hoy_dt.strftime("%Y-%m-%d %H:%M")

    # 2. Guardar para la WEB (noticias.json)
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)

    # 3. Guardar en tu HDD de 1 TB (historico_noticias.csv)
    archivo_historial = 'historico_noticias.csv'
    existe = os.path.isfile(archivo_historial)
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Fecha', 'Categoria', 'Titulo', 'URL', 'Resumen'])
        for cat, data in noticias.items():
            writer.writerow([hoy_str, cat.upper(), data['titulo'], data['url'], data['resumen']])
    
    print(f"✅ Historial y Web actualizados ({hoy_str})")

    # 4. PUBLICACIÓN EN LINKEDIN (Lunes a Viernes, no festivos)
    if es_dia_laborable():
        # Elegimos una categoría al azar para el post de hoy
        cat_elegida = random.choice(list(noticias.keys()))
        noticia_para_post = noticias[cat_elegida]
        
        print(f"🚀 Iniciando publicación en LinkedIn (Categoría: {cat_elegida})...")
        publicar_en_linkedin(noticia_para_post)
    else:
        print("😴 Hoy es festivo o fin de semana. No se publica en LinkedIn.")

if __name__ == "__main__":
    ejecutar_flujo()
