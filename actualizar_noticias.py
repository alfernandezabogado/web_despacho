import feedparser
import requests
import json
import os
import csv
from datetime import datetime

# --- CONFIGURACIÓN ---
CATEGORIAS = {
    "FAMILIA": "https://news.google.com/rss/search?q=sentencia+custodia+compartida+España+when:24h&hl=es&gl=ES&ceid=ES:es",
    "PENAL": "https://news.google.com/rss/search?q=derecho+penal+España+actualidad+when:24h&hl=es&gl=ES&ceid=ES:es",
    "MERCANTIL": "https://news.google.com/rss/search?q=concurso+acreedores+España+noticias+when:24h&hl=es&gl=ES&ceid=ES:es",
    "EXTRANJERIA": "https://news.google.com/rss/search?q=reforma+reglamento+extranjería+España+when:24h&hl=es&gl=ES&ceid=ES:es"
}

HISTORICO_FILE = 'historico_noticias.csv'
JSON_FILE = 'noticias.json'

# --- 1. FUNCIONES DE APOYO ---

def noticia_ya_publicada(url_nueva):
    """Evita duplicados en el CSV."""
    if not os.path.exists(HISTORICO_FILE): return False
    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return any(len(fila) > 3 and url_nueva == fila[3] for fila in reader)

def guardar_en_historico(categoria, titulo, url):
    """Guarda la noticia con fecha y hora exacta."""
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(HISTORICO_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([ahora, categoria, titulo, url])

# --- 2. LA FUNCIÓN CLAVE QUE PEDÍAS ---

def obtener_ultimas_del_historico():
    """Extrae la noticia más reciente de cada categoría del histórico."""
    ultimas = {}
    if not os.path.exists(HISTORICO_FILE):
        return ultimas

    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for fila in reader:
            if len(fila) >= 4:
                fecha_str, cat, titulo, url = fila[0], fila[1], fila[2], fila[3]
                # Al recorrer todo el archivo, el último registro de cada categoría 
                # machaca al anterior, dejándonos siempre con lo más nuevo.
                ultimas[cat] = {
                    "titulo": titulo.split(' - ')[0],
                    "resumen": f"Últimas novedades legislativas en {cat.capitalize()}. Información actualizada según la base de datos de nuestro despacho.",
                    "url": url,
                    "fecha": fecha_str  # Esta es la fecha que usaremos en la web
                }
    return ultimas

# --- 3. LÓGICA DE EJECUCIÓN ---

def buscar_nuevas_noticias():
    """Busca en Google News y alimenta el CSV si hay algo nuevo."""
    print("🔎 Buscando novedades en Google News...")
    for cat, url_rss in CATEGORIAS.items():
        feed = feedparser.parse(url_rss)
        for entrada in feed.entries:
            if not noticia_ya_publicada(entrada.link):
                titulo_limpio = entrada.title.split(' - ')[0]
                guardar_en_historico(cat, titulo_limpio, entrada.link)
                print(f"🆕 Nueva noticia guardada para {cat}")
                break # Solo guardamos la primera nueva que encontremos por categoría

def ejecutar_sincronizacion():
    print("🤖 Iniciando proceso de sincronización...")
    
    # Primero: Alimentamos el histórico con lo que haya hoy
    buscar_nuevas_noticias()
    
    # Segundo: Leemos el histórico para construir el JSON de la web
    datos_finales = obtener_ultimas_del_historico()
    
    if datos_finales:
        # Añadimos una marca de cuándo se sincronizó el sistema por última vez
        datos_finales["fecha_sistema"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, ensure_ascii=False, indent=4)
        print(f"✅ Web actualizada con éxito con datos del histórico.")
    else:
        print("❌ Error: El histórico está vacío.")

if __name__ == "__main__":
    ejecutar_sincronizacion()
