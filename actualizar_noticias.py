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
    # Búsquedas específicas para evitar que se repitan noticias entre categorías
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
                    # Extraemos el resumen original y limpiamos etiquetas HTML
                    resumen_sucio = entry.summary.split('<')[0] if 'summary' in entry else ""
                    
                    # --- SOLUCIÓN A LA DUPLICIDAD EN LA WEB ---
                    # Si el resumen es igual al título o muy corto, generamos un texto nuevo
                    # Esto evita que aparezca el mismo texto en negrita y en pequeño
                    if len(resumen_sucio) < 50 or titulo[:40] in resumen_sucio:
                        resumen_final = (
                            f"Analizamos las últimas novedades legislativas y jurisprudenciales en materia de Derecho {cat.capitalize()}. "
                            f"Esta actualización es fundamental para entender la evolución normativa actual en España sobre este asunto."
                        )
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
            noticias[cat] = {"titulo": f"Actualidad {cat}", "resumen": "Novedades del sector jurídico.", "url": "https://noticias.juridicas.com"}
    return noticias

def ejecutar_flujo():
    print("🤖 Iniciando actualización de noticias...")
    noticias = buscar_datos_ia()
    
    # 1. Guardar el JSON para la web (ahora con textos diferenciados)
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)
    print("✅ Web actualizada (noticias.json).")

    # 2. Publicar en LinkedIn solo si es laborable
    if es_dia_laborable():
        cat_elegida = random.choice(list(noticias.keys()))
        print(f"🚀 Publicando en LinkedIn categoría: {cat_elegida}")
        publicar_en_linkedin(noticias[cat_elegida])
    else:
        print("😴 Hoy es festivo o fin de semana. No se publica en LinkedIn.")

if __name__ == "__main__":
    ejecutar_flujo()
