import os
import json
import csv
from datetime import datetime

def actualizar_fuentes_juridicas():
    hoy = datetime.now().strftime('%d/%m/%Y')
    hoy_url = datetime.now().strftime('%Y%m%d')
    
    # Estructura lista para recibir datos reales (RSS o Scraping)
    # Ahora mismo son enlaces institucionales, pero el formato es el correcto
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
            # OJO: Esto falla si no hay BOE (festivos/finde)
            "url": f"https://www.boe.es/diario_boe/pdf.php?id=BOE-S-{hoy_url}"
        },
        "extranjeria": {
            "titulo": f"Ministerio: Actualidad Extranjería - {hoy}",
            "url": "https://extranjeros.inclusion.gob.es/"
        }
    }

    try:
        # 1. Guardar JSON para la WEB
        with open('noticias.json', 'w', encoding='utf-8') as f:
            json.dump(noticias, f, ensure_ascii=False, indent=4)
        print("✅ JSON actualizado correctamente.")

        # 2. Guardar Histórico CSV
        archivo_historial = 'historico_noticias.csv'
        existe = os.path.isfile(archivo_historial)
        
        with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not existe:
                writer.writerow(['Fecha', 'Categoria', 'Titulo', 'URL'])
            
            fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M")
            for cat, data in noticias.items():
                writer.writerow([fecha_registro, cat.upper(), data['titulo'], data['url']])
        
        print("✅ Histórico CSV actualizado correctamente.")

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")

if __name__ == "__main__":
    actualizar_fuentes_juridicas()
