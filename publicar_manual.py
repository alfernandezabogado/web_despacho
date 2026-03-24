import json
import os
import sys

# Archivos de intercambio con el YAML
JSON_FILE = 'noticias.json'
TEXTO_FILE = 'texto_ready.txt'
URL_FILE = 'url_ready.txt'

def preparar_manual(categoria_elegida):
    if not os.path.exists(JSON_FILE):
        print("Error: No existe noticias.json")
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    cat_upper = categoria_elegida.upper()
    if cat_upper not in datos:
        print(f"Error: La categoría {cat_upper} no está en el JSON.")
        return

    noticia = datos[cat_upper]
    titulo = noticia['titulo'].split(' - ')[0].split(' | ')[0].strip()
    
    # Redacción fija pero profesional para envío manual
    texto = (
        f"⚖️ {titulo}\n\n"
        f"Actualización relevante en materia de Derecho {categoria_elegida.capitalize()}.\n\n"
        f"Comparto esta información por su especial interés para el sector jurídico y profesional.\n\n"
        f"¿Qué os parece esta novedad? 👇\n\n"
        f"#Derecho #Abogacía #{categoria_elegida.capitalize()} #ActualidadJuridica"
    )

    with open(TEXTO_FILE, 'w', encoding='utf-8') as f:
        f.write(texto)
    with open(URL_FILE, 'w', encoding='utf-8') as f:
        f.write(noticia['url'])
    
    print(f"✅ Preparada noticia de {cat_upper} para publicar.")

if __name__ == "__main__":
    # Recibe la categoría como argumento desde GitHub Actions
    if len(sys.argv) > 1:
        preparar_manual(sys.argv[1])
