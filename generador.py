import json
from datetime import datetime

def generar_bloque_noticia():
    print("--- Generador de Noticias JSON v55 ---")
    
    # 1. Selección de área (para asegurar que coincida con tus botones HTML)
    areas_validas = ["FAMILIA", "PENAL", "MERCANTIL", "EXTRANJERIA"]
    print(f"Áreas disponibles: {', '.join(areas_validas)}")
    area = input("Introduce el área: ").upper().strip()
    
    if area not in areas_validas:
        print(f"⚠️ Advertencia: '{area}' no es un área estándar del sitio.")

    # 2. Recolección de datos
    titulo = input("Título de la noticia: ").strip()
    resumen = input("Resumen (máx 200 caracteres recomendado): ").strip()
    url = input("URL de la fuente original: ").strip()
    
    # 3. Fecha automática (Formato español)
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    ahora = datetime.now()
    fecha_formateada = f"{ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"

    # 4. Creación del diccionario
    noticia_dict = {
        area: {
            "titulo": titulo,
            "resumen": resumen,
            "fecha": fecha_formateada,
            "url": url
        }
    }

    # 5. Salida en formato JSON
    json_ready = json.dumps(noticia_dict, indent=4, ensure_ascii=False)
    
    print("\n✅ Bloque generado con éxito. Copia esto en tu noticias.json:\n")
    print(json_ready)
    print("\n--------------------------------------")

if __name__ == "__main__":
    generar_bloque_noticia()
