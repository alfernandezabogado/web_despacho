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
    
    # Lista de festivos nacionales 2026
    festivos_2026 = ["2026-01-01", "2026-01-06", "2026-04-03", "2026-05-01", "2026-10-12", "2026-12-25"]
    if ahora.strftime("%Y-%m-%d") in festivos_2026:
        return False
        
    return True

def publicar_en_linkedin(noticia):
    token = os.getenv('LINKEDIN_TOKEN')
    # Tu ID de miembro verificado en el paso anterior
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
    
    try:
        response = requests.post(url_api, headers=headers, json=payload)
        if response.status_code == 201:
            print("🚀 ¡Noticia publicada con éxito en LinkedIn!")
        else:
            print(f"❌ Error al publicar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def limpiar_resumen(texto):
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
        except:
            noticias[cat] = {"titulo": f"Actualidad {cat}", "resumen": "Consulta las novedades en el enlace.", "url": "https://noticias.juridicas.com"}
    return noticias

def ejecutar_flujo():
    # 1. Obtenemos las noticias
    noticias = buscar_datos_ia()
    hoy_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 2. Guardar para la WEB (noticias.json)
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)

    # 3. Guardar histórico para tu HDD de 1 TB
    archivo_historial = 'historico_noticias.csv'
    existe = os.path.isfile(archivo_historial)
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Fecha', 'Categoria', 'Titulo', 'URL', 'Resumen'])
        for cat, data in noticias.items():
            writer.writerow([hoy_str, cat.upper(), data['titulo'], data['url'], data['resumen']])
    
    print(f"✅ Web e Historial actualizados ({hoy_str})")

    # 4. Publicar en LinkedIn solo si es laborable
    if es_dia_laborable():
        cat_elegida = random.choice(list(noticias.keys()))
        print(f"🚀 Publicando categoría: {cat_elegida}")
        publicar_en_linkedin(noticias[cat_elegida])
    else:
        print("😴 Hoy no es laborable. No se publica en LinkedIn.")

if __name__ == "__main__":
    ejecutar_flujo()
