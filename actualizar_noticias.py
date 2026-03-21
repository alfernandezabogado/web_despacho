import feedparser
import json
import os
import csv
import random
from datetime import datetime

# --- CONFIGURACIÓN ---
CATEGORIAS = {
    "FAMILIA": "https://news.google.com/rss/search?q=sentencia+OR+reforma+derecho+familia+España+OR+custodia+compartida+when:48h&hl=es&gl=ES&ceid=ES:es",
    "PENAL": "https://news.google.com/rss/search?q=sentencia+OR+tribunal+derecho+penal+España+-opinión+-tribuna+-política+when:24h&hl=es&gl=ES&ceid=ES:es",
    "MERCANTIL": "https://news.google.com/rss/search?q=concurso+acreedores+España+noticias+mercantil+when:24h&hl=es&gl=ES&ceid=ES:es",
    "EXTRANJERIA": "https://news.google.com/rss/search?q=reforma+reglamento+extranjería+España+OR+BOE+when:24h&hl=es&gl=ES&ceid=ES:es"
}

HISTORICO_FILE = 'historico_noticias.csv'
JSON_FILE = 'noticias.json'
POST_LINKEDIN_FILE = 'ultimo_post_linkedin.txt'

def noticia_ya_publicada(url_nueva):
    if not os.path.exists(HISTORICO_FILE): return False
    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        return any(url_nueva in line for line in f)

def guardar_en_historico(categoria, titulo, url):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(HISTORICO_FILE, mode='a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([ahora, categoria, titulo, url])

def obtener_ultimas_del_historico():
    ultimas = {}
    if not os.path.exists(HISTORICO_FILE): return {}
    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        for fila in csv.reader(f):
            if len(fila) >= 4:
                ultimas[fila[1]] = {"titulo": fila[2], "url": fila[3], "fecha": fila[0]}
    return ultimas

def redactar_post_profesional(categoria, noticia):
    # Variantes de ganchos iniciales para evitar penalización de algoritmo
    ganchos = [
        "⚖️ NOVEDAD JURÍDICA:",
        "📢 ACTUALIDAD LEGAL:",
        "🔍 ANÁLISIS JURISPRUDENCIAL:",
        "🚀 ÚLTIMA HORA EN DERECHO:"
    ]
    
    # Variantes de cuerpo profesional
    cuerpos = [
        "Mantenerse al día con la jurisprudencia reciente es clave para ofrecer soluciones legales precisas.",
        "La interpretación de los tribunales evoluciona constantemente. Analizamos las últimas actualizaciones.",
        "El conocimiento actualizado del sector marca la diferencia en la estrategia de defensa legal.",
        "Comparto esta actualización relevante para profesionales y clientes del sector jurídico."
    ]

    gancho = random.choice(ganchos)
    cuerpo = random.choice(cuerpos)
    
    # Limpieza profunda del título (quita periódicos y separadores)
    titulo_limpio = noticia['titulo'].split(' - ')[0].split(' | ')[0].strip().upper()

    return (
        f"{gancho} {categoria.upper()}\n\n"
        f"📌 {titulo_limpio}\n\n"
        f"{cuerpo}\n\n"
        f"🔹 Área: {categoria.capitalize()}\n"
        f"🔹 Acceso a la noticia completa aquí:\n"
        f"👇\n{noticia['url']}\n\n"
        f"#Derecho #Abogacía #{categoria.capitalize()} #ActualidadJuridica #España"
    )

def ejecutar_sincronizacion():
    # 1. Scraping de nuevas noticias
    for cat, url_rss in CATEGORIAS.items():
        try:
            feed = feedparser.parse(url_rss)
            if not feed.entries:
                continue
                
            for entrada in feed.entries:
                if not noticia_ya_publicada(entrada.link):
                    # Guardamos solo el título limpio en el histórico para el CSV
                    titulo_corto = entrada.title.split(' - ')[0].strip()
                    guardar_en_historico(cat, titulo_corto, entrada.link)
                    break # Solo una noticia nueva por categoría cada vez
        except Exception as e:
            print(f"Error procesando {cat}: {e}")

    # 2. Generar JSON para la web
    datos = obtener_ultimas_del_historico()
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

    # 3. Selección y redacción para LinkedIn
    # Elegimos una categoría al azar de las que tengan noticias guardadas hoy
    candidatas = [c for c in CATEGORIAS.keys() if c in datos]
    if candidatas:
        cat_elegida = random.choice(candidatas)
        texto = redactar_post_profesional(cat_elegida, datos[cat_elegida])
        
        with open(POST_LINKEDIN_FILE, 'w', encoding='utf-8') as f:
            f.write(texto)
        print(f"Post redactado con éxito para la categoría: {cat_elegida}")
    else:
        print("No hay noticias nuevas para redactar hoy.")

if __name__ == "__main__":
    ejecutar_sincronizacion()
