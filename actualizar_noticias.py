import os
import json
import csv
import feedparser  # <--- CRÍTICO: Necesitas instalar esto (pip install feedparser)
from datetime import datetime

def actualizar_fuentes_juridicas():
    hoy = datetime.now().strftime('%d/%m/%Y')
    
    # DEFINICIÓN DE CONCEPTOS: Aquí es donde el bot decide qué buscar
    conceptos = {
        "familia": "sentencia+custodia+compartida+España",
        "penal": "sentencia+Tribunal+Supremo+penal+España",
        "mercantil": "BOE+resolucion+concursal+noticias",
        "extranjeria": "reforma+reglamento+extranjeria+España"
    }
    
    noticias = {}

    # MOTOR DE BÚSQUEDA
    for cat, busqueda in conceptos.items():
        try:
            # Buscamos en el RSS de Google News por el concepto específico
            url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es&gl=ES&ceid=ES:es"
            feed = feedparser.parse(url_rss)
            
            if feed.entries:
                # Si encuentra algo, cogemos la noticia más reciente
                noticias[cat] = {
                    "titulo": feed.entries[0].title,
                    "url": feed.entries[0].link
                }
            else:
                raise Exception("Sin resultados")
        except:
            # Si la búsqueda falla, usamos tu enlace institucional de reserva
            noticias[cat] = {
                "titulo": f"Actualidad {cat.capitalize()} - {hoy}",
                "url": "https://noticias.juridicas.com"
            }

    try:
        # 1. Guardar JSON para la WEB (Usando 'url' para evitar undefined)
        with open('noticias.json', 'w', encoding='utf-8') as f:
            json.dump(noticias, f, ensure_ascii=False, indent=4)
        
        # 2. Guardar Histórico CSV (Para tu HDD de 1 TB)
        archivo_historial = 'historico_noticias.csv'
        existe = os.path.isfile(archivo_historial)
        with open(archivo_historial, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not existe:
                writer.writerow(['Fecha', 'Categoria', 'Titulo', 'URL'])
            
            fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M")
            for cat, data in noticias.items():
                writer.writerow([fecha_registro, cat.upper(), data['titulo'], data['url']])
        
        print(f"✅ Búsqueda completada y archivos actualizados para el {hoy}.")

    except Exception as e:
        print(f"❌ Error durante la grabación de datos: {e}")

if __name__ == "__main__":
    actualizar_fuentes_juridicas()
