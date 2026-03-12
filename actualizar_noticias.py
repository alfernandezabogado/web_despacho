import os
import json
import csv
from datetime import datetime

def ejecutar_flujo_rescate():
    # Fecha para las URLs y títulos
    hoy = datetime.now().strftime('%d/%m/%Y')
    hoy_url = datetime.now().strftime('%Y%m%d')

    # Diccionario con nombres exactos para tu WEB y LinkedIn
    noticias = {
        "familia": {
            "titulo": f"TS: Jurisprudencia Familia - {hoy}",
            "url": "https://www.poderjudicial.es/search/index.jsp"
        },
        "penal": {
            "titulo": f"TS: Jurisprudencia Penal - {hoy}",
            "url": "https://www.poderjudicial.es/search/index.jsp"
        },
        "mercantil": {
            "titulo": f"BOE: Sumario de Resoluciones - {hoy}",
            "url": f"https://www.boe.es/diario_boe/pdf.php?id=BOE-S-{hoy_url}"
        },
        "extranjeria": {
            "titulo": f"Ministerio: Actualidad Extranjería - {hoy}",
            "url": "https://extranjeros.inclusion.gob.es/"
        }
    }

    # 1. Actualizar JSON (Adiós al 'undefined' en la web)
    with open('noticias.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)

    # 2. Actualizar CSV (Para tu copia de seguridad de 1 TB)
    archivo_historial = 'historico_noticias.csv'
    existe = os.path.isfile(archivo_historial)
    with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['Fecha', 'Categoria', 'Titulo', 'URL'])
        for cat, data in noticias.items():
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), cat.upper(), data['titulo'], data['url']])

if __name__ == "__main__":
    ejecutar_flujo_rescate()
