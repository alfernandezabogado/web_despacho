import json
import os
import sys

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
    # Limpiamos el título para que no salgan nombres de periódicos
    titulo = noticia['titulo'].split(' - ')[0].split(' | ')[0].strip()
    
    # Redacción profesional sin la URL pegada (la URL irá en la tarjeta)
    texto = (
        f"⚖️ {titulo}\n\n"
        f"Actualización de especial interés en Derecho {categoria_elegida.capitalize()}.\n\n"
        f"Analizamos los puntos clave de esta novedad jurisprudencial y su impacto.\n\n"
        f"¿Qué opináis sobre este criterio? 👇\n\n"
        f"#Derecho #Abogacía #{categoria_elegida.capitalize()} #ActualidadJuridica"
    )

    with open(TEXTO_FILE, 'w', encoding='utf-8') as f:
        f.write(texto)
    with open(URL_FILE, 'w', encoding='utf-8') as f:
        f.write(noticia['url'])
    
    print(f"✅ Preparada noticia de {cat_upper}: {titulo}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        preparar_manual(sys.argv[1])
