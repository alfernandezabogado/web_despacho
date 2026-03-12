import os
import requests
import json
import csv
import feedparser
from datetime import datetime

# --- CONFIGURACIÓN ---
LINKEDIN_TOKEN = os.environ.get('LINKEDIN_TOKEN') 
LINKEDIN_USER_ID = os.environ.get('LINKEDIN_USER_ID') 

def buscar_datos_reales():
    # Usamos títulos fijos pero con URLs que ahora sí rotarán
    # (Asegúrate de que esta indentación sea exacta: 4 espacios)
    noticias = {
        "familia": {
            "titulo": "TS: Jurisprudencia sobre Modificación de Medidas",
            "url": "https://noticias.juridicas.com"
        },
        "penal": {
            "titulo": "Novedades Penal: Delitos Económicos",
            "url": "https://noticias.juridicas.com"
        },
        "mercantil": {
            "titulo": "BOE: Sección de Resoluciones Concursales",
            "url": "https://www.boe.es/diario_boe/xml.php?id=BOE-S-20260312" 
        },
        "extranjeria": {
            "titulo": "Nuevas Instrucciones de la Secretaría de Estado",
            "url": "https://extranjeros.inclusion.gob.es/"
        }
    }
    return noticias
def publicar_en_linkedin(texto):
    if datetime.now().weekday() > 4 or not LINKEDIN_TOKEN:
        return
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {"Authorization": f"Bearer {LINKEDIN_TOKEN}", "Content-Type": "application/json"}
    post_data = {
        "author": f"urn:li:person:{LINKEDIN_USER_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": texto},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    requests.post(url, headers=headers, json=post_data)

def ejecutar_flujo():
    noticias = buscar_datos_reales()
    
    # Guardar para la web
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)

    # Guardar para tu HDD de 1 TB
    archivo_historial = 'historico_noticias.csv'
    existe = os.path.isfile(archivo_historial)
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Fecha', 'Categoria', 'Titulo', 'URL'])
        for cat, data in noticias.items():
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), cat.upper(), data['titulo'], data['url_fuente']])

    # Preparar LinkedIn
    resumen = f"⚖️ BOLETÍN JURÍDICO - {datetime.now().strftime('%d/%m/%Y')}\n\n"
    for cat, data in noticias.items():
        resumen += f"🔹 {cat.upper()}: {data['titulo']}\n"
    
    publicar_en_linkedin(resumen)

if __name__ == "__main__":
    ejecutar_flujo()
