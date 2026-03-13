import os
import json
import csv
import feedparser
import requests
import random
from datetime import datetime

def es_dia_laborable():
    ahora = datetime.now()
    if ahora.weekday() > 4:
        return False
    festivos_2026 = ["2026-01-01", "2026-01-06", "2026-04-03", "2026-05-01", "2026-10-12", "2026-12-25"]
    if ahora.strftime("%Y-%m-%d") in festivos_2026:
        return False
    return True

def publicar_en_linkedin(noticia):
    token = os.getenv('LINKEDIN_TOKEN')
    mi_id_urn = "urn:li:person:5mzvpwns6H" 
    
    url_api = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    
    texto_post = (
        f"📌 ACTUALIDAD Y NOVEDADES JURÍDICAS\n\n"
        f"⚖️ {noticia['titulo'].upper()}\n\n"
        f"Comparto esta información relevante de última hora:\n\n"
        f"\" {noticia['resumen']} \"\n\n"
        f"🔗 Análisis completo en el siguiente enlace:\n"
        f"{noticia['url']}\n\n"
        "Espero que les resulte de utilidad. #Derecho #Abogacia #Actualidad"
    )

    payload = {
        "author": mi_id_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": texto_post},
                "shareMediaCategory": "ARTICLE",
                "media": [{"status": "READY", "originalUrl": noticia['url']}]
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    requests.post(url_api, headers=headers, json=payload)

def buscar_datos_ia():
    # Definimos búsquedas mucho más específicas para evitar solapamientos
    conceptos = {
        "familia": "sentencia+custodia+compartida+divorcio+España", 
        "penal": "delito+codigo+penal+sentencia+audiencia+nacional",
        "mercantil": "concurso+acreedores+sociedades+mercantil+España",
        "extranjeria": "visado+residencia+arraigo+ley+extranjeria+España"
    }
    
    noticias = {}
    urls_usadas = set() # Para evitar que una noticia se repita en varias categorías

    for cat, busqueda in conceptos.items():
        try:
            url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es&gl=ES&ceid=ES:es"
            feed = feedparser.parse(url_rss)
            
            noticia_encontrada = False
            for entry in feed.entries:
                if entry.link not in urls_usadas:
                    resumen = entry.summary.split('<')[0] if 'summary' in entry else entry.title
                    if len(resumen) < 50: resumen = entry.title
                    
                    noticias[cat] = {
                        "titulo": entry.title,
                        "resumen": resumen[:400],
                        "url": entry.link
                    }
                    urls_usadas.add(entry.link)
                    noticia_encontrada = True
                    break
            
            if not noticia_encontrada:
                raise Exception("No hay noticias nuevas para esta categoría")

        except Exception as e:
            noticias[cat] = {
                "titulo": f"Actualidad en Derecho {cat.capitalize()}", 
                "resumen": f"Revisión de las últimas novedades normativas en materia {cat}.", 
                "url": "https://noticias.juridicas.com"
            }
    return noticias

def ejecutar_flujo():
    noticias = buscar_datos_ia()
    
    # 1. Actualizar JSON para la web (con contenido diferenciado)
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)
    print("✅ Web actualizada con contenidos únicos por categoría.")

    # 2. Publicar en LinkedIn
    if es_dia_laborable():
        cat_elegida = random.choice(list(noticias.keys()))
        publicar_en_linkedin(noticias[cat_elegida])
        print(f"🚀 Publicado en LinkedIn: {cat_elegida}")

if __name__ == "__main__":
    ejecutar_flujo()
