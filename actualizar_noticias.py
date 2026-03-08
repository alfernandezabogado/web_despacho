import os
import requests
from bs4 import BeautifulSoup
import json
import csv
import smtplib
from datetime import datetime
from email.message import EmailMessage

# --- CONFIGURACIÓN DE SEGURIDAD (GitHub Secrets) ---
# Usamos os.environ para no dejar la contraseña a la vista en el código
EMAIL_EMISOR = "despachofernandezsanz@gmail.com"
EMAIL_RECEPTOR = "despachofernandezsanz@gmail.com"
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD') # Lee el Secret de GitHub

def enviar_notificacion(categoria, titulo, url):
    """Envía un email cuando se localiza un documento."""
    if not EMAIL_PASSWORD:
        print("❌ Error: No se encontró la contraseña en las variables de entorno.")
        return

    msg = EmailMessage()
    msg['Subject'] = f"⚖️ ALERTA LEGAL: {categoria.upper()}"
    msg['From'] = EMAIL_EMISOR
    msg['To'] = EMAIL_RECEPTOR
    
    contenido = f"""
    Hola Ángel,
    
    El bot ha localizado una nueva actualización para tu despacho:
    
    📌 TÍTULO: {titulo}
    📂 CATEGORÍA: {categoria.upper()}
    🔗 ENLACE: {url}
    
    Los archivos noticias.json y el historial se han actualizado.
    """
    msg.set_content(contenido)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_EMISOR, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"📧 Email enviado: {categoria}")
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")

def buscar_datos_reales():
    """Simula la extracción de CENDOJ y BOE (Estructura para scraping)"""
    fecha_hoy = datetime.now().strftime("%d de %B, %Y")
    
    # Aquí es donde el bot usará requests y BeautifulSoup para navegar
    # Por ahora definimos la estructura que alimentará tu web y tu HDD
    noticias = {
        "familia": {
            "titulo": "TS: Doctrina sobre Custodia y Distancia",
            "cuerpo": "Sentencia reciente del Tribunal Supremo (Sala 1)...",
            "fecha": fecha_hoy,
            "url_fuente": "https://www.poderjudicial.es/search/index.jsp" # URL real CENDOJ
        },
        "penal": {
            "titulo": "TS: Criterios sobre Prueba Digital",
            "cuerpo": "Jurisprudencia actualizada Sala 2...",
            "fecha": fecha_hoy,
            "url_fuente": "https://www.poderjudicial.es/search/index.jsp"
        },
        "boe": {
            "titulo": "BOE: Disposiciones de Derecho Civil",
            "cuerpo": "Novedades legislativas publicadas hoy...",
            "fecha": fecha_hoy,
            "url_fuente": f"https://www.boe.es/diario_boe/xml.php?id=BOE-S-{datetime.now().strftime('%Y%m%d')}"
        },
        "extranjeria": {
            "titulo": "Interior: Instrucciones Arraigo",
            "cuerpo": "Actualización de trámites de extranjería...",
            "fecha": fecha_hoy,
            "url_fuente": "https://extranjeros.inclusion.gob.es/"
        }
    }
    return noticias

def ejecutar_flujo():
    nuevas_noticias = buscar_datos_reales()
    
    # 1. Enviar avisos
    for cat, data in nuevas_noticias.items():
        enviar_notificacion(cat, data['titulo'], data['url_fuente'])

    # 2. Actualizar noticias.json (Para la Web)
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(nuevas_noticias, f, ensure_ascii=False, indent=4)

    # 3. Actualizar historico_noticias.csv (Para tu HDD de 1 TB)
    archivo_historial = 'historico_noticias.csv'
    existe = os.path.isfile(archivo_historial)
    
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Fecha_Registro', 'Categoria', 'Titulo', 'URL'])
        
        for cat, data in nuevas_noticias.items():
            writer.writerow([datetime.now(), cat.upper(), data['titulo'], data['url_fuente']])

if __name__ == "__main__":
    ejecutar_flujo()
