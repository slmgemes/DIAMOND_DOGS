import json
from pathlib import Path

EXTENSION = ".model.json"
CAMPOS = (
    "version_formato", "descripcion", "columnas_entrada", "columna_salida",
    "coeficientes", "termino_independiente", "formula", "metricas",
)

def agregar_extension(ruta):
    """Devuelve la ruta con la extensión de los archivos de modelo (.model.json).

    Si el nombre ya termina en .model.json no se cambia. Si termina en .json,
    se sustituye por .model.json. En cualquier otro caso se añade al final.

    Parameters
    ----------
    ruta : str or Path
        Ruta elegida por el usuario.

    Returns
    -------
    Path
        Ruta con la extensión .model.json.

    Raises
    ------
    ValueError
        Si la ruta no incluye un nombre de archivo.
    """
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
    """Indica si ya existe el archivo que se crearía con esa ruta.

    Se comprueba la ruta con la extensión añadida, que es la que se guarda.

    Parameters
    ----------
    ruta : str or Path
        Ruta elegida por el usuario.

    Returns
    -------
    bool
        True si el archivo ya existe y se sobrescribiría.
    """
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

    faltan = [campo for campo in CAMPOS if campo not in datos_modelo]
    if faltan:
        raise ValueError("Faltan campos en la información del modelo: " + ", ".join(faltan) + ".")

    datos = {campo: datos_modelo[campo] for campo in CAMPOS}
    ruta = agregar_extension(ruta)
    texto = json.dumps(datos, indent=4, ensure_ascii=False)

    try:
        ruta.write_text(texto, encoding="utf-8")
    except PermissionError as e:
        raise ValueError(f"No hay permisos para guardar en la carpeta elegida: {ruta.parent}") from e
    except FileNotFoundError as e:
        raise ValueError(f"La carpeta elegida no existe: {ruta.parent}") from e
    except OSError as e:
        raise ValueError(f"No se pudo guardar el modelo: {e}") from e

    return ruta
