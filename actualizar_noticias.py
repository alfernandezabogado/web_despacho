import json
import datetime
import csv
import os

# 1. SIMULACIÓN DE AGENTE DE BÚSQUEDA JURÍDICA
# En una fase avanzada, aquí conectaríamos con APIs de BOE o CENDOJ.
# Por ahora, definimos la estructura que alimentará tu web hoy.

def generar_noticias_del_dia():
    fecha_hoy = datetime.datetime.now().strftime("%d de %B, %Y")
    
    noticias = {
        "familia": {
            "titulo": "Custodia Compartida y Distancia Geográfica",
            "cuerpo": "El Tribunal Supremo unifica doctrina: la distancia entre domicilios solo es obstáculo si impide el desarrollo normal de la vida del menor, priorizando la corresponsabilidad.",
            "fecha": fecha_hoy,
            "url_fuente": "https://www.poderjudicial.es/search/index.jsp"
        },
        "penal": {
            "titulo": "Prueba Digital en el Proceso Penal",
            "cuerpo": "Nuevas directrices sobre la cadena de custodia en capturas de pantalla de aplicaciones de mensajería. Se requiere pericial técnica en caso de impugnación de autenticidad.",
            "fecha": fecha_hoy,
            "url_fuente": "https://www.boe.es"
        },
        "mercantil": {
            "titulo": "Responsabilidad de Administradores",
            "cuerpo": "Clarificación sobre el deber de diligencia: la insolvencia de la sociedad no implica automáticamente la responsabilidad personal si se acredita la solicitud de concurso en plazo.",
            "fecha": fecha_hoy,
            "url_fuente": "https://www.cnmv.es"
        },
        "extranjeria": {
            "titulo": "Arraigo para la Formación: Novedades",
            "cuerpo": "Instrucciones actualizadas sobre los cursos habilitados para la prórroga de residencia. Se amplía el catálogo de centros oficiales autorizados por el Ministerio.",
            "fecha": fecha_hoy,
            "url_fuente": "https://extranjeros.inclusion.gob.es/"
        }
    }
    return noticias

def actualizar_archivos():
    nuevas_noticias = generar_noticias_del_dia()
    
    # --- PARTE A: ACTUALIZAR LA WEB (SOBRESCRITURA) ---
    # Esto es lo que lee el index.html cada día
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(nuevas_noticias, f, ensure_ascii=False, indent=4)
    print("✅ noticias.json actualizado para la web.")

    # --- PARTE B: GUARDAR EL HISTORIAL (ACUMULACIÓN) ---
    # Esto es para tu control personal. Crea un CSV si no existe y añade la línea.
    archivo_historial = 'historico_noticias.csv'
    existe_archivo = os.path.isfile(archivo_historial)
    
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Si es nuevo, ponemos cabeceras
        if not existe_archivo:
            writer.writerow(['Fecha', 'Categoría', 'Título', 'Enlace Fuente'])
        
        # Añadimos las 4 noticias de hoy al historial
        for cat, data in nuevas_noticias.items():
            writer.writerow([data['fecha'], cat.upper(), data['titulo'], data['url_fuente']])
    
    print(f"✅ Historial actualizado en {archivo_historial}.")

if __name__ == "__main__":
    actualizar_archivos()
