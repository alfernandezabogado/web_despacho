import json
import datetime

# Diccionario base con las áreas del despacho
noticias = {
    "familia": {
        "titulo": "Actualidad en Custodia Compartida - Marzo 2026",
        "cuerpo": "El Tribunal Supremo refuerza el derecho de los menores a mantener la estabilidad en su entorno habitual tras el divorcio, priorizando el interés superior del niño en las sentencias más recientes.",
        "fecha": datetime.datetime.now().strftime("%d de %B, %Y")
    },
    "penal": {
        "titulo": "Reformas en Seguridad Vial",
        "cuerpo": "Novedades legislativas endurecen las sanciones administrativas por distracciones al volante. Es vital conocer los nuevos márgenes de interpretación judicial.",
        "fecha": datetime.datetime.now().strftime("%d de %B, %Y")
    },
    "mercantil": {
        "titulo": "Responsabilidad de Administradores",
        "cuerpo": "La nueva jurisprudencia aclara los límites de la responsabilidad personal en sociedades limitadas ante deudas imprevistas. Proteja su patrimonio empresarial.",
        "fecha": datetime.datetime.now().strftime("%d de %B, %Y")
    },
    "extranjeria": {
        "titulo": "Agilización de Nacionalidad Española",
        "cuerpo": "Justicia implementa nuevos procesos digitales para reducir los tiempos de espera en los expedientes de nacionalidad por residencia durante este trimestre.",
        "fecha": datetime.datetime.now().strftime("%d de %B, %Y")
    }
}

# Generación del archivo JSON que consume la web
with open('noticias.json', 'w', encoding='utf-8') as f:
    json.dump(noticias, f, ensure_ascii=False, indent=2)

print("v51: Archivo noticias.json actualizado con éxito.")
