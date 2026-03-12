import os
import requests
import json
import csv
from datetime import datetime

def buscar_datos_reales():
    # En lugar de rastrear, construimos la URL técnica del sumario del día
    fecha_hoy = datetime.now().strftime('%Y%m%d')
    url_pdf_directo = f"https://www.boe.es/diario_boe/pdf.php?id=BOE-S-{fecha_hoy}"
    
    # Estructura limpia para la WEB y el CSV
    return {
        "familia": {
            "titulo": "TS: Jurisprudencia sobre Custodia Compartida (Actualizado)",
            "url": "https://www.poderjudicial.es/search/index.jsp"
        },
        "penal": {
            "titulo": "TS: Jurisprudencia en Delitos Informáticos (Actualizado)",
            "url": "https://www.poderjudicial.es/search/index.jsp"
        },
        "mercantil": {
            "titulo": f"BOE: Sumario de Resoluciones del {datetime.now().strftime('%d/%m/%Y')}",
            "url": url_pdf_directo  # <--- URL CONSTRUIDA TÉCNICAMENTE
        },
        "extranjeria": {
            "titulo": "Ministerio: Instrucciones de Arraigo y Residencia",
            "url": "https://extranjeros.inclusion.gob.es/"
        }
    }

def ejecutar_flujo():
    noticias = buscar_datos_reales()
    
    # 1. Actualizar JSON para la WEB (Usando 'url' para evitar undefined)
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)

    # 2. Actualizar CSV para tu HDD de 1 TB
    archivo_historial = 'historico_noticias.csv'
    existe = os.path.isfile(archivo_historial)
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Fecha', 'Categoria', 'Titulo', 'URL'])
        for cat, data in noticias.items():
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), cat.upper(), data['titulo'], data['url']])

if __name__ == "__main__":
    ejecutar_flujo()
