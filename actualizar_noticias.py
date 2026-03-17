import feedparser
import requests
import json
import os
import csv
import random
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

def noticia_ya_publicada(url_nueva):
    """Consulta el historial para evitar repetir la misma noticia."""
    if not os.path.exists(HISTORICO_FILE):
        return False
    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for fila in reader:
            if len(fila) > 3 and url_nueva == fila[3]:
                return True
    return False

def guardar_en_historico(categoria, titulo, url):
    """Registra la noticia con timestamp para auditoría."""
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    file_exists = os.path.isfile(HISTORICO_FILE)
    with open(HISTORICO_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([ahora, categoria, titulo, url])

def buscar_noticias():
    """Busca noticias frescas y filtra las que ya existen en el CSV."""
    noticias_del_dia = {}
    
    for cat, url_rss in CATEGORIAS.items():
        feed = feedparser.parse(url_rss)
        noticia_encontrada = False
        
        for entrada in feed.entries:
            if not noticia_ya_publicada(entrada.link):
                # Limpiamos el título (quitamos la fuente al final)
                titulo_limpio = entrada.title.split(' - ')[0]
                
                noticias_del_dia[cat] = {
                    "titulo": titulo_limpio,
                    "resumen": f"Últimas novedades legislativas y jurisprudenciales en materia de {cat.capitalize()}. Esta información es clave para entender la evolución normativa actual en España.",
                    "url": entrada.link
                }
                # Guardamos en el CSV nada más encontrarla para "bloquearla"
                guardar_en_historico(cat, titulo_limpio, entrada.link)
                noticia_encontrada = True
                break
        
        # Si no hay nada nuevo en las últimas 24h, mantenemos un mensaje de cortesía
        if not noticia_encontrada:
            print(f"⚠️ No hay noticias nuevas para {cat}. Se mantendrá la última conocida.")

    return noticias_del_dia

def ejecutar_flujo():
    print("🤖 Iniciando actualización de noticias...")
    
    hoy = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Verificar si ya se actualizó hoy (Lógica de Congelación Diaria)
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            try:
                datos_actuales = json.load(f)
                if datos_actuales.get("fecha_actualizacion") == hoy:
                    print(f"🛑 Noticias ya actualizadas hoy ({hoy}). Finalizando para evitar duplicados.")
                    return
            except json.JSONDecodeError:
                pass

    # 2. Buscar nuevas noticias
    nuevas_noticias = buscar_noticias()
    
    if nuevas_noticias:
        nuevas_noticias["fecha_actualizacion"] = hoy
        
        # 3. Guardar el JSON para la web (compatible con v51)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(nuevas_noticias, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Archivo {JSON_FILE} actualizado correctamente.")
        
        # 4. Opcional: Publicar una de ellas en LinkedIn (puedes añadir aquí tu lógica de Token)
        # cat_random = random.choice(list(CATEGORIAS.keys()))
        # publicar_en_linkedin(nuevas_noticias[cat_random])

if __name__ == "__main__":
    ejecutar_flujo()
