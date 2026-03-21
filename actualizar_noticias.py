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
    # 1. Limpieza de título (evitamos gritos en mayúsculas y nombres de diarios)
    titulo = noticia['titulo'].split(' - ')[0].split(' | ')[0].strip()
    
    # 2. Variantes de cuerpo para que no parezca un bot
    cuerpos = [
        "Mantenerse al día con la jurisprudencia reciente es clave para ofrecer soluciones legales precisas.",
        "La interpretación de los tribunales evoluciona constantemente. Analizamos esta actualización.",
        "El conocimiento actualizado del sector marca la diferencia en la estrategia legal.",
        "Comparto esta novedad relevante para profesionales y clientes del sector jurídico."
    ]
    
    cuerpo_elegido = random.choice(cuerpos)

    # 3. Formateamos el texto (Sin la URL al final para que no ensucie)
    texto = (
        f"⚖️ {titulo}\n\n"
        f"Actualización en Derecho de {categoria.capitalize()}.\n\n"
        f"{cuerpo_elegido}\n\n"
        f"¿Qué opináis sobre este criterio? Os leo. 👇\n\n"
        f"#Derecho #Abogacía #{categoria.capitalize()} #ActualidadJuridica"
    )
    
    # Devolvemos el texto y la URL por separado
    return texto, noticia['url']

def ejecutar_sincronizacion():
    # 1. Scraping
    for cat, url_rss in CATEGORIAS.items():
        try:
            feed = feedparser.parse(url_rss)
            for entrada in feed.entries:
                if not noticia_ya_publicada(entrada.link):
                    titulo_corto = entrada.title.split(' - ')[0].strip()
                    guardar_en_historico(cat, titulo_corto, entrada.link)
                    break 
        except Exception as e:
            print(f"Error en {cat}: {e}")

    # 2. JSON para web
    datos = obtener_ultimas_del_historico()
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

    # 3. Preparación para LinkedIn (Texto + URL en líneas separadas)
    candidatas = [c for c in CATEGORIAS.keys() if c in datos]
    if candidatas:
        cat_elegida = random.choice(candidatas)
        texto_post, url_noticia = redactar_post_profesional(cat_elegida, datos[cat_elegida])
        
        # Guardamos el texto y en la ÚLTIMA LÍNEA la URL (importante para el YAML)
        with open(POST_LINKEDIN_FILE, 'w', encoding='utf-8') as f:
            f.write(texto_post + "\n" + url_noticia)
    else:
        print("Sin noticias nuevas.")

if __name__ == "__main__":
    ejecutar_sincronizacion()
