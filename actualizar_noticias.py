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
    conceptos = {
        "familia": "sentencia+custodia+compartida+España", 
        "penal": "delito+codigo+penal+España",
        "mercantil": "concurso+acreedores+España",
        "extranjeria": "ley+extranjeria+arraigo+España"
    }
    noticias = {}
    urls_usadas = set()

    for cat, busqueda in conceptos.items():
        try:
            url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es&gl=ES&ceid=ES:es"
            feed = feedparser.parse(url_rss)
            
            for entry in feed.entries:
                if entry.link not in urls_usadas:
                    titulo = entry.title
                    # Extraemos el resumen y quitamos HTML
                    resumen_sucio = entry.summary.split('<')[0] if 'summary' in entry else ""
                    
                    # --- FILTRO ANTI-REPETICIÓN ---
                    # Si el resumen es igual al título o muy corto, generamos una frase profesional
                    if len(resumen_sucio) < 40 or titulo[:30] in resumen_sucio:
                        resumen_final = f"Nueva actualización relevante en el ámbito de Derecho {cat.capitalize()}. Esta resolución marca un punto de interés para el despacho y nuestros clientes por su impacto en la normativa actual."
                    else:
                        resumen_final = resumen_sucio[:350]

                    noticias[cat] = {
                        "titulo": titulo,
                        "resumen": resumen_final,
                        "url": entry.link
                    }
                    urls_usadas.add(entry.link)
                    break
        except:
            noticias[cat] = {"titulo": f"Actualidad {cat}", "resumen": "Consulta las últimas novedades del sector en el enlace adjunto.", "url": "https://noticias.juridicas.com"}
    return noticias

def ejecutar_flujo():
    noticias = buscar_datos_ia()
    
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)
    print("✅ Web actualizada con contenidos únicos.")

    if es_dia_laborable():
        cat_elegida = random.choice(list(noticias.keys()))
        publicar_en_linkedin(noticias[cat_elegida])
        print(f"🚀 Publicado en LinkedIn: {cat_elegida}")

if __name__ == "__main__":
    ejecutar_flujo()
