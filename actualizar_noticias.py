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
    # Recuperamos el token de los secretos de GitHub (Paso 2)
    token = os.getenv('LINKEDIN_TOKEN')
    
    # Tu ID de miembro obtenido en el "Token Generator"
    # IMPORTANTE: Sustituye esto por tu URN real (ej: urn:li:person:abc123XYZ)
    mi_id_urn = "AQVOo0165Bhv0bn5nUuM2TRlG9JwHeUFjuxG8PHkKPap8GYn1h0SoD0A3nVVMf3MdLkAKxKyNZJlBkMJPJst8jRa-1Z4LDT2Cd93VFqhsFy1C0vZmVl5JNDkPTA__KTRK-arTvJGQkJJYuTr4PgzCZ5vawJ_TykjLYLcBYTfuDqoCTJE1drJFjwZd7UKPkG1iVS0sY6rzpgXNy42NCoXjWmqZWdYO8zxvaGNS3DVa18wOE40w7ALeZXx6d3pdzCskA6QeOaDJ46i1uIfeEGgC53ZzLf9_hyaEQoCcCBrEIioUvqvPRAffEqvz5aIanjz6VgKr4AP8-r887zeFv8bem9GsZL8tA" 
    
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
        "#Derecho #Abogacia #ActualidadJuridica"
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
            print("✅ ¡Publicado en LinkedIn con éxito!")
        else:
            print(f"❌ Error al publicar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
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
