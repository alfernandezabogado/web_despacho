import feedparser
import requests
import json
import os
import csv
import random
from datetime import datetime

# --- CONFIGURACIÓN OPTIMIZADA (Filtro Anti-Opinión y Política) ---
CATEGORIAS = {
    "FAMILIA": "https://news.google.com/rss/search?q=sentencia+OR+reforma+derecho+familia+España+OR+custodia+compartida+when:48h&hl=es&gl=ES&ceid=ES:es",
    "PENAL": "https://news.google.com/rss/search?q=sentencia+OR+tribunal+derecho+penal+España+-opinión+-tribuna+-política+when:24h&hl=es&gl=ES&ceid=ES:es",
    "MERCANTIL": "https://news.google.com/rss/search?q=concurso+acreedores+España+noticias+mercantil+when:24h&hl=es&gl=ES&ceid=ES:es",
    "EXTRANJERIA": "https://news.google.com/rss/search?q=reforma+reglamento+extranjería+España+OR+BOE+when:24h&hl=es&gl=ES&ceid=ES:es"
}

HISTORICO_FILE = 'historico_noticias.csv'
JSON_FILE = 'noticias.json'
LOG_LINKEDIN = 'log_linkedin.txt'
POST_LINKEDIN_FILE = 'ultimo_post_linkedin.txt' # Nuevo: para que GitHub Actions lea el texto

# --- 1. FUNCIONES DE APOYO ---

def noticia_ya_publicada(url_nueva):
    if not os.path.exists(HISTORICO_FILE): return False
    try:
        with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
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

# --- 2. LÓGICA DE REDACCIÓN Y PUBLICACIÓN ---

def redactar_post_profesional(categoria, noticia):
    """Genera un texto persuasivo para LinkedIn evitando el formato frío"""
    titulo = noticia['titulo'].upper()
    url = noticia['url']
    
    cuerpo = (
        f"🚀 {titulo}\n\n"
        f"⚖️ ACTUALIDAD JURÍDICA: {categoria.capitalize()}\n"
        f"Analizar la jurisprudencia reciente es vital para anticipar soluciones legales efectivas. "
        f"Hoy destacamos esta novedad en materia de {categoria.lower()}:\n\n"
        f"🔹 Impacto en procedimientos y estrategias legales.\n"
        f"🔹 Claves de la reciente actualización del sector.\n\n"
        f"🔍 En el ejercicio del derecho, el conocimiento actualizado marca la diferencia para proteger tus intereses.\n\n"
        f"👇 Consulta la noticia completa aquí:\n"
        f"{url}\n\n"
        f"#Abogado #Derecho #ActualidadJuridica #{categoria.capitalize()} #AngelLuisFernandez"
    )
    return cuerpo

def obtener_ultima_categoria_linkedin():
    if os.path.exists(LOG_LINKEDIN):
        with open(LOG_LINKEDIN, 'r') as f:
            return f.read().strip()
    return None

def registrar_publicacion_linkedin(categoria, texto_post):
    with open(LOG_LINKEDIN, 'w') as f:
        f.write(categoria)
    # Guardamos el texto en un archivo temporal para que GitHub Actions pueda leerlo
    with open(POST_LINKEDIN_FILE, 'w', encoding='utf-8') as f:
        f.write(texto_post)

def elegir_noticia_para_linkedin(datos_finales):
    ultima_cat = obtener_ultima_categoria_linkedin()
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
                    titulo_limpio = entrada.title.split(' - ')[0].strip()
                    guardar_en_historico(cat, titulo_limpio, entrada.link)
                    print(f"✅ Nueva noticia detectada en {cat}")
                    break
        except Exception as e:
            print(f"❌ Error rastreando {cat}: {e}")

def ejecutar_sincronizacion():
    print(f"🚀 Ejecutando Bot de Actualización: {datetime.now()}")
    
    buscar_nuevas_noticias()
    
    datos_finales = obtener_ultimas_del_historico()
    datos_finales["fecha_sistema"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos_finales, f, ensure_ascii=False, indent=4)
    
    cat_link, noticia_link = elegir_noticia_para_linkedin(datos_finales)
    if cat_link:
        print(f"🎯 Noticia seleccionada para LinkedIn: {cat_link}")
        # REDACTAR EL POST CON EL NUEVO FORMATO
        texto_para_linkedin = redactar_post_profesional(cat_link, noticia_link)
        registrar_publicacion_linkedin(cat_link, texto_para_linkedin)
        print("📝 Post redactado y listo para envío.")
        
    print("✅ Proceso completado con éxito.")

if __name__ == "__main__":
    ejecutar_sincronizacion()
