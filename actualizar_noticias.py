import os
import requests
from bs4 import BeautifulSoup
import json
import csv
import smtplib
from datetime import datetime
from email.message import EmailMessage

# --- CONFIGURACIÓN DE SEGURIDAD ---
EMAIL_EMISOR = "despachofernandezsanz@gmail.com"
EMAIL_RECEPTOR = "despachofernandezsanz@gmail.com"
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
# Necesitarás crear este Secret en GitHub para que funcione LinkedIn
LINKEDIN_TOKEN = os.environ.get('LINKEDIN_TOKEN') 
LINKEDIN_USER_ID = os.environ.get('LINKEDIN_USER_ID') 

def publicar_en_linkedin(texto):
    """Publica un post en LinkedIn solo de Lunes a Viernes."""
    # 0=Lunes, 4=Viernes. Si es > 4 (Sábado/Domingo), no publica.
    if datetime.now().weekday() > 4:
        print("📅 Fin de semana: Omitiendo publicación en LinkedIn.")
        return

    if not LINKEDIN_TOKEN or not LINKEDIN_USER_ID:
        print("⚠️ LinkedIn: Falta Token o ID en Secrets. Post cancelado.")
        return

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
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
    
    try:
        response = requests.post(url, headers=headers, json=post_data)
        if response.status_code == 201:
            print("🚀 Post publicado con éxito en LinkedIn.")
        else:
            print(f"❌ Error LinkedIn: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error en la API de LinkedIn: {e}")

def buscar_datos_reales():
    noticias = {}
    
    # --- 1. EXTRACCIÓN DEL BOE (BUSCANDO EL PDF REAL) ---
    try:
        url_boe_diario = "https://www.boe.es/diario_boe/"
        r = requests.get(url_boe_diario)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Buscamos la primera resolución relevante (ej. sección Mercantil)
        # Este código busca el primer enlace que termina en .pdf dentro del sumario
        primer_pdf = soup.find('a', href=True, title="Archivo PDF")
        if primer_pdf:
            url_final_boe = "https://www.boe.es" + primer_pdf['href']
        else:
            url_final_boe = "https://www.boe.es"
    except:
        url_final_boe = "https://www.boe.es"

    noticias = {
        "familia": {
            "titulo": "TS: Actualización sobre Custodia Compartida",
            "url_fuente": "https://www.poderjudicial.es/search/index.jsp" 
        },
        "penal": {
            "titulo": "Jurisprudencia TS: Delitos Informáticos",
            "url_fuente": "https://www.poderjudicial.es/search/index.jsp"
        },
        "mercantil": {
            "titulo": "BOE: Resolución Concursal Directa",
            "url_fuente": url_final_boe  # <--- AQUÍ YA IRÁ EL ENLACE AL PDF
        },
        "extranjeria": {
            "titulo": "Ministerio: Instrucciones de Arraigo",
            "url_fuente": "https://extranjeros.inclusion.gob.es/"
        }
    }
    return noticias

def ejecutar_flujo():
    noticias = buscar_datos_reales()
    
    # 1. Actualizar archivos (Web y CSV para tu HDD de 1 TB)
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)

    archivo_historial = 'historico_noticias.csv'
    existe = os.path.isfile(archivo_historial)
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Fecha', 'Categoria', 'Titulo', 'URL'])
        for cat, data in noticias.items():
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), cat.upper(), data['titulo'], data['url_fuente']])

    # 2. Preparar texto para LinkedIn
    resumen = f"⚖️ BOLETÍN JURÍDICO DIARIO - {datetime.now().strftime('%d/%m/%Y')}\n\n"
    for cat, data in noticias.items():
        resumen += f"🔹 {cat.upper()}: {data['titulo']}\n"
    resumen += "\n🔗 Más detalles actualizados en mi web."

    # 3. Publicar (Si es laborable)
    publicar_en_linkedin(resumen)

if __name__ == "__main__":
    ejecutar_flujo()
