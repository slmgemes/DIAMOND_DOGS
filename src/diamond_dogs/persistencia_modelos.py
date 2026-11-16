import json
from pathlib import Path
import numpy as np

VERSION_FORMATO = 1
EXTENSION = ".model.json"

def agregar_extension(ruta):
    ruta = Path(ruta)
    nombre = ruta.name
    if not nombre:
        raise ValueError("El nombre del archivo está vacío.")
    if nombre.lower().endswith(EXTENSION):
        return ruta
    if nombre.lower().endswith(".json"):
        nombre = nombre[:-len(".json")]
    return ruta.with_name(nombre + EXTENSION)

def existe_archivo(ruta):
    return agregar_extension(ruta).exists()


def guardar_modelo(ruta, datos_modelo):
    """Guarda la información del modelo en un archivo .model.json.

    Solo se escriben los campos de la estructura documentada (CAMPOS), aunque
    datos_modelo tenga más: así nunca se guardan datos ni gráficos.

    Parameters
    ----------
    ruta : str or Path
        Ruta del archivo. Si no termina en .model.json, se añade.
    datos_modelo : dict
        Información del modelo, tal como la devuelve crear_datos_modelo.

    Returns
    -------
    Path
        Ruta del archivo guardado, con la extensión añadida.

    Raises
    ------
    ValueError
        Si faltan campos en la información del modelo o no se puede escribir
        el archivo (carpeta inexistente, sin permisos...). El mensaje es
        apto para mostrarlo al usuario.
    """

    ruta = Path(ruta)
    ruta.write_text(json.dumps(datos_modelo, indent=4, ensure_ascii=False), encoding="utf-8")
    return ruta
