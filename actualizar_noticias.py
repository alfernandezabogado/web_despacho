import json
import datetime

# Por ahora simulamos la extracción de Derecho de Familia
# En la fase final, aquí conectaremos con la API de noticias jurídicas
noticia_nueva = {
    "familia": {
        "titulo": "Nueva Sentencia sobre Custodia en Extremadura",
        "cuerpo": "El Tribunal ha ratificado que la proximidad domiciliaria es clave para la custodia compartida, afectando a procesos en curso en la provincia de Cáceres.",
        "fecha": datetime.datetime.now().strftime("%d de %B, %Y")
    }
}

# Guardamos el resultado en el JSON que lee tu web
with open('noticias.json', 'w', encoding='utf-8') as f:
    json.dump(noticia_nueva, f, ensure_ascii=False, indent=2)
