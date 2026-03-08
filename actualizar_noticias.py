import json
import datetime
import csv
import os
import smtplib
from email.message import EmailMessage

# --- CONFIGURACIÓN DE EMAIL ---
EMAIL_EMISOR = "despachofernandezsanz@gmail.com"
EMAIL_RECEPTOR = "despachofernandezsanz@gmail.com"
# Contraseña de Aplicación de 16 letras
EMAIL_PASSWORD = "yfym yfzv hdne senq" 

def enviar_notificacion(categoria, titulo, url):
    """Envía un email solo si se localiza un PDF directo."""
    msg = EmailMessage()
    msg['Subject'] = f"⚖️ SENTENCIA LOCALIZADA: {categoria.upper()}"
    msg['From'] = EMAIL_EMISOR
    msg['To'] = EMAIL_RECEPTOR
    
    contenido = f"""
    Hola Ángel,
    
    El bot de madrugada ha localizado un documento oficial:
    
    📌 TÍTULO: {titulo}
    📂 CATEGORÍA: {categoria.upper()}
    🔗 ENLACE PDF: {url}
    
    Este enlace se ha actualizado automáticamente en noticias.json.
    """
    msg.set_content(contenido)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_EMISOR, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"📧 Email enviado para la categoría: {categoria}")
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")

def generar_noticias_del_dia():
    fecha_hoy = datetime.datetime.now().strftime("%d de %B, %Y")
    
    noticias = {
        "familia": {
            "titulo": "Custodia Compartida y Distancia Geográfica",
            "cuerpo": "El Tribunal Supremo unifica doctrina...",
            "fecha": fecha_hoy,
            "url_fuente": "https://www.poderjudicial.es/ejemplo.pdf" 
        },
        "penal": {
            "titulo": "Prueba Digital en el Proceso Penal",
            "cuerpo": "Nuevas directrices sobre la cadena de custodia...",
            "fecha": fecha_hoy,
            "url_fuente": "https://www.boe.es/ejemplo.pdf"
        },
        "mercantil": {
            "titulo": "Responsabilidad de Administradores",
            "cuerpo": "Clarificación sobre el deber de diligencia...",
            "fecha": fecha_hoy,
            "url_fuente": "https://www.cnmv.es"
        },
        "extranjeria": {
            "titulo": "Arraigo para la Formación: Novedades",
            "cuerpo": "Instrucciones actualizadas...",
            "fecha": fecha_hoy,
            "url_fuente": "https://extranjeros.inclusion.gob.es/"
        }
    }
    return noticias

def actualizar_archivos():
    nuevas_noticias = generar_noticias_del_dia()
    
    # --- PROCESO DE ENVÍO DE EMAIL ---
    for cat, data in nuevas_noticias.items():
        if data['url_fuente'].lower().endswith('.pdf'):
            enviar_notificacion(cat, data['titulo'], data['url_fuente'])

    # --- PARTE A: ACTUALIZAR LA WEB ---
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(nuevas_noticias, f, ensure_ascii=False, indent=4)
    print("✅ noticias.json actualizado.")

    # --- PARTE B: HISTORIAL (Almacenamiento en frío) ---
    archivo_historial = 'historico_noticias.csv' 
    # Para usar tu HDD de 1 TB: archivo_historial = 'D:/historico_noticias.csv'
    
    existe_archivo = os.path.isfile(archivo_historial)
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe_archivo:
            writer.writerow(['Fecha', 'Categoría', 'Título', 'Enlace Fuente'])
            
        for cat, data in nuevas_noticias.items():
            writer.writerow([data['fecha'], cat.upper(), data['titulo'], data['url_fuente']])
    
    print(f"✅ Historial actualizado en {archivo_historial}.")

if __name__ == "__main__":
    actualizar_archivos()
