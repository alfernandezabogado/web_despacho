import json
import os
import feedparser # Necesitarás instalar esta librería: pip install feedparser
from datetime import datetime

def limpiar_titulo(titulo):
    # Quita el nombre del periódico al final (ej: " - El País")
    return titulo.split(' - ')[0].split(' | ')[0].strip()

def obtener_noticias_automaticas():
    # URLs configuradas solo para ESPAÑA
    busquedas = {
        "PENAL": "https://news.google.com/rss/search?q=derecho+penal+España+when:24h&hl=es&gl=ES&ceid=ES:es",
        "MERCANTIL": "https://news.google.com/rss/search?q=derecho+mercantil+España+when:24h&hl=es&gl=ES&ceid=ES:es",
        "FAMILIA": "https://news.google.com/rss/search?q=derecho+familia+España+when:24h&hl=es&gl=ES&ceid=ES:es",
        "EXTRANJERIA": "https://news.google.com/rss/search?q=extranjería+España+when:24h&hl=es&gl=ES&ceid=ES:es"
    }

    archivo_json = 'noticias.json'
    data = {}

    print("--- ⚖️ ACTUALIZADOR AUTOMÁTICO DE NOTICIAS (ESPAÑA) ---")

    for categoria, url in busquedas.items():
        print(f"Buscando {categoria}...")
        feed = feedparser.parse(url)
        
        if feed.entries:
            # Tomamos la primera noticia que devuelva Google
            primera = feed.entries[0]
            
            # Filtro de seguridad por si se cuelan dominios extranjeros (.cl, .ar, etc)
            if any(dom in primera.link for dom in [".cl/", ".ar/", ".mx/", ".co/"]):
                print(f"⚠️ Noticia extranjera descartada en {categoria}. Saltando...")
                continue

            data[categoria] = {
                "titulo": limpiar_titulo(primera.title),
                "url": primera.link,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        else:
            print(f"❌ No se han encontrado noticias hoy para {categoria}")

    # Guardar en el JSON
    with open(archivo_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print("\n✅ noticias.json actualizado con éxito.")

if __name__ == "__main__":
    obtener_noticias_automaticas()
