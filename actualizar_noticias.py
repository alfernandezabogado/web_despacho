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
    # Intentamos leer la llave desde los Secrets de GitHub
    token = os.getenv('LINKEDIN_TOKEN')
    
    if not token:
        print("❌ ERROR: No he encontrado el secreto 'LINKEDIN_TOKEN' en GitHub Settings.")
        return

    # --- BLOQUE PARA EXTRAER TU ID ---
    url_id = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        res = requests.get(url_id, headers=headers)
        if res.status_code == 200:
            datos = res.json()
            # ESTO ES LO QUE NECESITAS COPIAR DEL LOG
            print(f"🎯 TU ID ES: urn:li:person:{datos['sub']}")
        else:
            print(f"❌ ERROR DE AUTENTICACIÓN: {res.status_code}")
            print(f"Respuesta de LinkedIn: {res.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def limpiar_resumen(texto):
    if not texto: return "Sin descripción."
    return texto.split('<')[0] if "<" in texto else texto

def buscar_datos_ia():
    conceptos = {"familia": "sentencia+custodia+compartida+España", "penal": "Tribunal+Supremo+penal+España"}
    noticias = {}
    for cat, busqueda in conceptos.items():
        try:
            url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es&gl=ES&ceid=ES:es"
            feed = feedparser.parse(url_rss)
            if feed.entries:
                entry = random.choice(feed.entries[:3])
                noticias[cat] = {
                    "titulo": entry.title,
                    "resumen": limpiar_resumen(entry.summary if 'summary' in entry else entry.title)[:150] + "...",
                    "url": entry.link
                }
        except:
            noticias[cat] = {"titulo": f"Actualidad {cat}", "resumen": "Novedades del sector.", "url": "https://noticias.juridicas.com"}
    return noticias

def ejecutar_flujo():
    noticias = buscar_datos_ia()
    print("✅ Noticias obtenidas correctamente.")

    if es_dia_laborable():
        cat_elegida = random.choice(list(noticias.keys()))
        print(f"🚀 Intentando obtener ID para publicar categoría: {cat_elegida}")
        publicar_en_linkedin(noticias[cat_elegida])
    else:
        print("😴 Hoy no es día laborable.")

if __name__ == "__main__":
    ejecutar_flujo()
