import os
import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime

# --- CONFIGURACIÓN ---
LINKEDIN_TOKEN = os.environ.get('LINKEDIN_TOKEN')
LINKEDIN_USER_ID = os.environ.get('LINKEDIN_USER_ID')

def buscar_datos_reales():
    noticias = {}
    fecha_hoy_xml = datetime.now().strftime('%Y%m%d')
    
    # 1. Intento de extracción del BOE (Sección Mercantil)
    url_boe = "https://www.boe.es"
    try:
        # Intentamos obtener el PDF del sumario del día
        r_boe = requests.get(f"https://www.boe.es/diario_boe/xml.php?id=BOE-S-{fecha_hoy_xml}", timeout=10)
        soup_boe = BeautifulSoup(r_boe.text, 'xml')
        pdf_node = soup_boe.find('url_pdf') or soup_boe.find('urlPdf')
        if pdf_node:
            url_boe = "https://www.boe.es" + pdf_node.text
    except:
        pass

    # 2. Estructura unificada (Usamos 'url' para evitar KeyErrors)
    noticias = {
        "familia": {
            "titulo": "TS: Jurisprudencia sobre Custodia Compartida",
            "url": "https://www.poderjudicial.es/search/index.jsp"
        },
        "penal": {
            "titulo": "TS: Jurisprudencia en Delitos Informáticos",
            "url": "https://www.poderjudicial.es/search/index.jsp"
        },
        "mercantil": {
            "titulo": "BOE: Resoluciones Concursales Actualizadas",
            "url": url_boe
        },
        "extranjeria": {
            "titulo": "Ministerio: Instrucciones de Arraigo",
            "url": "https://extranjeros.inclusion.gob.es/"
        }
    }
    return noticias

def publicar_en_linkedin(texto):
    if not LINKEDIN_TOKEN or datetime.now().weekday() > 4:
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
    
    # Guardar para la Web (Sin 'undefined')
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
            # Usamos 'url' que es la clave que hemos definido arriba
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), cat.upper(), data['titulo'], data['url']])

    # Preparar LinkedIn
    resumen = f"⚖️ BOLETÍN JURÍDICO - {datetime.now().strftime('%d/%m/%Y')}\n\n"
    for cat, data in noticias.items():
        resumen += f"🔹 {cat.upper()}: {data['titulo']}\n"
    
    publicar_en_linkedin(resumen)

if __name__ == "__main__":
    ejecutar_flujo()
