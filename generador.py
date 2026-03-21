import json
import os
from datetime import datetime

def actualizar_noticia():
    archivo_json = 'noticias.json'
    
    # 1. Cargar el archivo existente o crear uno base
    if os.path.exists(archivo_json):
        with open(archivo_json, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"FAMILIA": {}, "PENAL": {}, "MERCANTIL": {}, "EXTRANJERIA": {}}
    else:
        data = {"FAMILIA": {}, "PENAL": {}, "MERCANTIL": {}, "EXTRANJERIA": {}}

    print("\n--- ⚖️ Actualizador Jurídico v55 PRO ---")
    
    # 2. Selección de área
    areas_validas = ["FAMILIA", "PENAL", "MERCANTIL", "EXTRANJERIA"]
    print(f"Categorías: {', '.join(areas_validas)}")
    area = input("👉 Elige categoría: ").upper().strip()
    
    if area not in areas_validas:
        print(f"❌ Error: '{area}' no existe en la web.")
        return

    # 3. Datos de la noticia
    titulo = input("📝 Título: ").strip()
    resumen = input("📄 Resumen corto: ").strip()
    url = input("🔗 URL de la noticia: ").strip()
    
    # 4. Fecha automática (Formato v55)
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    ahora = datetime.now()
    fecha_formateada = f"{ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"

    # 5. Inyectar datos
    data[area] = {
        "titulo": titulo,
        "resumen": resumen,
        "fecha": fecha_formateada,
        "url": url
    }
    
    # Actualizar la fecha de última sincronización
    data["fecha_sistema"] = ahora.strftime("%Y-%m-%d %H:%M")

    # 6. Guardar cambios
    with open(archivo_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ ¡Éxito! '{archivo_json}' actualizado con la noticia de {area.capitalize()}.")

if __name__ == "__main__":
    actualizar_noticia()
