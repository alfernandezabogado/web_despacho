import feedparser
import requests
import json
import os
import csv
import random
from datetime import datetime

# --- CONFIGURACIÓN OPTIMIZADA ---
CATEGORIAS = {
    # Ampliamos a 48h y añadimos keywords para evitar que FAMILIA quede vacía
    "FAMILIA": "https://news.google.com/rss/search?q=sentencia+OR+reforma+derecho+familia+España+OR+custodia+compartida+when:48h&hl=es&gl=ES&ceid=ES:es",
    "PENAL": "https://news.google.com/rss/search?q=derecho+penal+España+actualidad+when:24h&hl=es&gl=ES&ceid=ES:es",
    "MERCANTIL": "https://news.google.com/rss/search?q=concurso+acreedores+España+noticias+when:24h&hl=es&gl=ES&ceid=ES:es",
    "EXTRANJERIA": "https://news.google.com/rss/search?q=reforma+reglamento+extranjería+España+when:24h&hl=es&gl=ES&ceid=ES:es"
}

HISTORICO_FILE = 'historico_noticias.csv'
JSON_FILE = 'noticias.json'
LOG_LINKEDIN = 'log_linkedin.txt'

# --- 1. FUNCIONES DE APOYO ---

def noticia_ya_publicada(url_nueva):
    if not os.path.exists(HISTORICO_FILE): return False
    try:
        with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Verificamos si la URL ya existe en nuestra base de datos CSV
            return any(len(fila) > 3 and url_nueva == fila[3] for fila in reader)
    except:
        return False

def guardar_en_historico(categoria, titulo, url):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(HISTORICO_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([ahora, categoria, titulo, url])

def obtener_ultimas_del_historico():
    ultimas = {}
    for cat in CATEGORIAS.keys():
        ultimas[cat] = {
            "titulo": f"Actualidad en {cat.capitalize()}",
            "resumen": f"Sincronizando novedades de {cat.lower()}...",
            "url": "",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    if not os.path.exists(HISTORICO_FILE): return ultimas
    
    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for fila in reader:
            if len(fila) >= 4:
                fecha_str, cat, titulo, url = fila[0], fila[1], fila[2], fila[3]
                if cat in ultimas:
                    ultimas[cat] = {
                        "titulo": titulo, 
                        "resumen": f"Últimas novedades legales en materia de {cat.lower()}.", 
                        "url": url, 
                        "fecha": fecha_str
                    }
    return ultimas

# --- 2. LÓGICA DE PUBLICACIÓN AUTOMÁTICA ---

def obtener_ultima_categoria_linkedin():
    if os.path.exists(LOG_LINKEDIN):
        with open(LOG_LINKEDIN, 'r') as f:
            return f.read().strip()
    return None

def registrar_publicacion_linkedin(categoria):
    with open(LOG_LINKEDIN, 'w') as f:
        f.write(categoria)

def elegir_noticia_para_linkedin(datos_finales):
    ultima_cat = obtener_ultima_categoria_linkedin()
    # Filtramos candidatas para no repetir la categoría de ayer
    candidatas = [cat for cat in CATEGORIAS.keys() if datos_finales[cat]["url"] != "" and cat != ultima_cat]
    
    if not candidatas:
        candidatas = [cat for cat in CATEGORIAS.keys() if datos_finales[cat]["url"] != ""]
    
    if not candidatas: return None, None
    
    cat_elegida = random.choice(candidatas)
    return cat_elegida, datos_finales[cat_elegida]

# --- 3. EJECUCIÓN PRINCIPAL ---

def buscar_nuevas_noticias():
    print("🔎 Iniciando rastreo en Google News...")
    for cat, url_rss in CATEGORIAS.items():
        try:
            feed = feedparser.parse(url_rss)
            for entrada in feed.entries:
                if not noticia_ya_publicada(entrada.link):
                    # Limpiamos el título para que no aparezca el nombre del medio
                    titulo_limpio = entrada.title.split(' - ')[0].strip()
                    guardar_en_historico(cat, titulo_limpio, entrada.link)
                    print(f"✅ Nueva noticia detectada en {cat}")
                    break
        except Exception as e:
            print(f"❌ Error rastreando {cat}: {e}")

def ejecutar_sincronizacion():
    print(f"🚀 Ejecutando Bot de Actualización: {datetime.now()}")
    
    # 1. Buscar y guardar en histórico CSV
    buscar_nuevas_noticias()
    
    # 2. Generar el JSON para la web v55
    datos_finales = obtener_ultimas_del_historico()
    datos_finales["fecha_sistema"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos_finales, f, ensure_ascii=False, indent=4)
    
    # 3. Preparar disparo para LinkedIn
    cat_link, noticia_link = elegir_noticia_para_linkedin(datos_finales)
    if cat_link:
        print(f"🎯 Noticia seleccionada para LinkedIn: {cat_link}")
        registrar_publicacion_linkedin(cat_link)
        
    print("✅ Proceso completado con éxito.")

if __name__ == "__main__":
    ejecutar_sincronizacion()
