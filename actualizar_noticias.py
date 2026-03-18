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
    with open(HISTORICO_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([ahora, categoria, titulo, url])

def recuperar_ultima_del_historico(categoria):
    """Busca la última noticia guardada de una categoría específica."""
    if not os.path.exists(HISTORICO_FILE):
        return None
    
    ultima_noticia = None
    with open(HISTORICO_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # Recorremos todo el historial para quedarnos con la última entrada de esa categoría
        for fila in reader:
            if len(fila) > 3 and fila[1] == categoria:
                ultima_noticia = {
                    "titulo": fila[2],
                    "resumen": f"Últimas novedades legislativas y jurisprudenciales en materia de {categoria.capitalize()}.",
                    "url": fila[3]
                }
    return ultima_noticia

def buscar_noticias():
    """Busca noticias frescas y aplica el respaldo si no hay novedades."""
    noticias_del_dia = {}
    
    for cat, url_rss in CATEGORIAS.items():
        feed = feedparser.parse(url_rss)
        noticia_encontrada = False
        
        for entrada in feed.entries:
            if not noticia_ya_publicada(entrada.link):
                titulo_limpio = entrada.title.split(' - ')[0]
                noticias_del_dia[cat] = {
                    "titulo": titulo_limpio,
                    "resumen": f"Últimas novedades legislativas y jurisprudenciales en materia de {cat.capitalize()}. Esta información es clave para entender la evolución normativa actual en España.",
                    "url": entrada.link
                }
                guardar_en_historico(cat, titulo_limpio, entrada.link)
                noticia_encontrada = True
                break
        
        # SI NO HAY NOTICIAS NUEVAS, USAMOS EL RESPALDO
        if not noticia_encontrada:
            print(f"⚠️ Buscando respaldo para {cat}...")
            respaldo = recuperar_ultima_del_historico(cat)
            if respaldo:
                noticias_del_dia[cat] = respaldo
                print(f"✅ Respaldo encontrado para {cat}")

    return noticias_del_dia

def ejecutar_flujo():
    print("🤖 Iniciando actualización de noticias...")
    hoy = datetime.now().strftime("%Y-%m-%d")
    
    # Lógica de Congelación Diaria
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            try:
                datos_actuales = json.load(f)
                if datos_actuales.get("fecha_actualizacion") == hoy:
                    print(f"🛑 Ya actualizado hoy ({hoy}).")
                    return
            except json.JSONDecodeError:
                pass

    nuevas_noticias = buscar_noticias()
    
    if nuevas_noticias:
        nuevas_noticias["fecha_actualizacion"] = hoy
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(nuevas_noticias, f, ensure_ascii=False, indent=4)
        print(f"✅ Archivo {JSON_FILE} actualizado.")

if __name__ == "__main__":
    ejecutar_flujo()
