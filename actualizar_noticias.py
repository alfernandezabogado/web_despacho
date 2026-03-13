import os
import json
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
    
    # Hemos ampliado el texto para que la publicación se vea "llena" y profesional
    # Añadimos una introducción y llamadas a la acción
    texto_post = (
        f"📌 ACTUALIDAD Y NOVEDADES JURÍDICAS\n\n"
        f"⚖️ {noticia['titulo'].upper()}\n\n"
        f"Comparto esta información relevante de última hora que afecta al sector:\n\n"
        f"\" {noticia['resumen']} \"\n\n"
        f"🔗 Pueden leer el análisis completo y los detalles en el siguiente enlace:\n"
        f"{noticia['url']}\n\n"
        "Espero que esta actualización les resulte de utilidad. Saludos.\n\n"
        "#Derecho #Abogacia #ActualidadJuridica #Justicia #España"
    )

    payload = {
        "author": mi_id_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": texto_post},
                "shareMediaCategory": "ARTICLE", # Cambiado de NONE a ARTICLE para forzar previsualización
                "media": [
                    {
                        "status": "READY",
                        "originalUrl": noticia['url']
                    }
                ]
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    res = requests.post(url_api, headers=headers, json=payload)
    if res.status_code == 201:
        print("🚀 ¡Post enriquecido publicado con éxito!")
    else:
        # Si el sitio original bloquea la previsualización de ARTICLE, reintentamos como texto simple
        print("⚠️ Reintentando con formato de texto simple...")
        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "NONE"
        del payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"]
        requests.post(url_api, headers=headers, json=payload)

def buscar_datos_ia():
    conceptos = {
        "familia": "sentencia+custodia+compartida+España", 
        "penal": "Tribunal+Supremo+penal+España",
        "civil": "novedad+juridica+España"
    }
    noticias = {}
    for cat, busqueda in conceptos.items():
        try:
            url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es&gl=ES&ceid=ES:es"
            feed = feedparser.parse(url_rss)
            if feed.entries:
                entry = random.choice(feed.entries[:5])
                # Limpiamos mejor el resumen para evitar el "..." tan corto
                resumen = entry.summary.split('<')[0] if 'summary' in entry else entry.title
                if len(resumen) < 50: resumen = entry.title
                
                noticias[cat] = {
                    "titulo": entry.title,
                    "resumen": resumen[:400], # Aumentamos el límite de texto
                    "url": entry.link
                }
        except:
            noticias[cat] = {"titulo": f"Novedad en {cat}", "resumen": "Actualización del ordenamiento jurídico.", "url": "https://noticias.juridicas.com"}
    return noticias

def ejecutar_flujo():
    noticias = buscar_datos_ia()
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)
    
    if es_dia_laborable():
        cat_elegida = random.choice(list(noticias.keys()))
        publicar_en_linkedin(noticias[cat_elegida])

if __name__ == "__main__":
    ejecutar_flujo()
