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
    # AQUÍ ESTÁ TU ID REAL
    mi_id_urn = "urn:li:person:5mzvpwns6H" 
    
    url_api = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    
    texto_post = (
        f"📢 ACTUALIDAD JURÍDICA\n\n"
        f"⚖️ {noticia['titulo']}\n\n"
        f"📝 {noticia['resumen']}\n\n"
        f"🔗 Noticia completa: {noticia['url']}\n\n"
        "#Derecho #Abogacia #Actualidad #Justicia"
    )

    payload = {
        "author": mi_id_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": texto_post},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    res = requests.post(url_api, headers=headers, json=payload)
    if res.status_code == 201:
        print("🚀 ¡Noticia publicada con éxito en LinkedIn!")
    else:
        print(f"❌ Error al publicar: {res.status_code} - {res.text}")

def limpiar_resumen(texto):
    if not texto: return "Sin descripción."
    return texto.split('<')[0] if "<" in texto else texto

def buscar_datos_ia():
    conceptos = {
        "familia": "sentencia+custodia+compartida+España", 
        "penal": "Tribunal+Supremo+penal+España",
        "civil": "reclamacion+clausula+suelo+España"
    }
    noticias = {}
    for cat, busqueda in conceptos.items():
        try:
            url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es&gl=ES&ceid=ES:es"
            feed = feedparser.parse(url_rss)
            if feed.entries:
                entry = random.choice(feed.entries[:5])
                noticias[cat] = {
                    "titulo": entry.title,
                    "resumen": limpiar_resumen(entry.summary if 'summary' in entry else entry.title)[:160] + "...",
                    "url": entry.link
                }
        except:
            noticias[cat] = {"titulo": f"Novedad en Derecho {cat}", "resumen": "Revisión de la actualidad semanal.", "url": "https://noticias.juridicas.com"}
    return noticias

def ejecutar_flujo():
    noticias = buscar_datos_ia()
    
    # 1. Guardamos en el JSON para la web
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)
    
    # 2. Publicamos en LinkedIn si es laborable
    if es_dia_laborable():
        cat_elegida = random.choice(list(noticias.keys()))
        print(f"🔄 Publicando categoría '{cat_elegida}' en LinkedIn...")
        publicar_en_linkedin(noticias[cat_elegida])
    else:
        print("😴 Fin de semana o festivo: No se publica en redes.")

if __name__ == "__main__":
    ejecutar_flujo()
