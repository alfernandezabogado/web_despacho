import json
import os
import subprocess
from datetime import datetime

def ejecutar_git():
    """Automatiza la subida a GitHub"""
    try:
        print("\n🚀 Subiendo cambios a GitHub...")
        subprocess.run(["git", "add", "noticias.json"], check=True)
        subprocess.run(["git", "commit", "-m", f"Actualización noticias {datetime.now().strftime('%d/%m/%Y')}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("\n✅ ¡WEB ACTUALIZADA EN VIVO!")
    except Exception as e:
        print(f"\n❌ Error al subir a GitHub: {e}")
        print("Asegúrate de tener Git instalado y haber hecho login.")

def actualizar_noticia():
    archivo_json = 'noticias.json'
    
    # Cargar datos existentes
    if os.path.exists(archivo_json):
        with open(archivo_json, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except: data = {"FAMILIA":{}, "PENAL":{}, "MERCANTIL":{}, "EXTRANJERIA":{}}
    else:
        data = {"FAMILIA":{}, "PENAL":{}, "MERCANTIL":{}, "EXTRANJERIA":{}}

    print("\n--- ⚖️ PANEL DE CONTROL JURÍDICO v55 ---")
    area = input("👉 Categoría (FAMILIA, PENAL, MERCANTIL, EXTRANJERIA): ").upper().strip()
    
    if area not in ["FAMILIA", "PENAL", "MERCANTIL", "EXTRANJERIA"]:
        print("❌ Categoría no válida.")
        return

    titulo = input("📝 Título: ").strip()
    resumen = input("📄 Resumen: ").strip()
    url = input("🔗 URL: ").strip()
    
    # Fecha automática
    ahora = datetime.now()
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    fecha_esp = f"{ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"

    data[area] = {"titulo": titulo, "resumen": resumen, "fecha": fecha_esp, "url": url}
    data["fecha_sistema"] = ahora.strftime("%Y-%m-%d %H:%M")

    # Guardar localmente
    with open(archivo_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Archivo guardado localmente.")
    
    # Lanzar subida automática
    ejecutar_git()

if __name__ == "__main__":
    actualizar_noticia()
