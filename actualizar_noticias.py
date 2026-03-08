import json
import datetime
import csv
import os
import smtplib
from email.message import EmailMessage

# --- CONFIGURACIÓN DE EMAIL ---
EMAIL_EMISOR = "tu_correo@gmail.com"
EMAIL_RECEPTOR = "tu_correo@gmail.com"
# Si usas Gmail, necesitas una "Contraseña de Aplicación" de 16 letras
EMAIL_PASSWORD = "tu_password_aqui" 

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
    
    # NOTA: Cambia estas URLs por enlaces .pdf reales para probar el envío
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
        # SOLO envía si el link es un PDF (Tu filtro de valor)
        if data['url_fuente'].lower().endswith('.pdf'):
            enviar_notificacion(cat, data['titulo'], data['url_fuente'])

    # --- PARTE A: ACTUALIZAR LA WEB ---
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(nuevas_noticias, f, ensure_ascii=False, indent=4)
    print("✅ noticias.json actualizado.")

    # --- PARTE B: HISTORIAL (Opcional: Guardar en HDD 1TB) ---
    archivo_historial = 'historico_noticias.csv' 
    # Aquí podrías poner 'D:/historico_noticias.csv' para usar tu HDD
    
    existe_archivo = os.path.isfile(archivo_historial)
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as
