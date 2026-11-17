import json
import math
from pathlib import Path
from diamond_dogs.crear_modelo import DatosModelo

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


def cargar_modelo(ruta: str | Path) -> DatosModelo:
    """Carga y valida un archivo de modelo en formato JSON.

    Raises
    ------
    ValueError
        Si el archivo no se puede leer o no contiene un modelo compatible.
    """
    ruta = Path(ruta)
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise ValueError(f"El archivo no existe: {ruta}") from e
    except PermissionError as e:
        raise ValueError(f"No hay permisos para leer el archivo: {ruta}") from e
    except (OSError, UnicodeError, json.JSONDecodeError) as e:
        raise ValueError(f"No se pudo cargar el modelo: {e}") from e

    if not isinstance(datos, dict):
        raise ValueError("El archivo no contiene un objeto de modelo válido.")

    faltan = [campo for campo in CAMPOS if campo not in datos]
    if faltan:
        raise ValueError("Faltan campos en el modelo: " + ", ".join(faltan) + ".")
    if (
        not isinstance(datos["version_formato"], int)
        or isinstance(datos["version_formato"], bool)
        or datos["version_formato"] != 1
    ):
        raise ValueError("La versión del formato del modelo no es compatible.")
    if not isinstance(datos["descripcion"], str):
        raise ValueError("La descripción del modelo debe ser texto.")
    if (
        not isinstance(datos["columnas_entrada"], list)
        or not datos["columnas_entrada"]
        or not all(isinstance(columna, str) and columna for columna in datos["columnas_entrada"])
        or len(set(datos["columnas_entrada"])) != len(datos["columnas_entrada"])
    ):
        raise ValueError("Las columnas de entrada del modelo no son válidas.")
    if not isinstance(datos["columna_salida"], str) or not datos["columna_salida"]:
        raise ValueError("La columna de salida del modelo no es válida.")
    if not isinstance(datos["formula"], str):
        raise ValueError("La fórmula del modelo debe ser texto.")

    coeficientes = datos["coeficientes"]
    if (
        not isinstance(coeficientes, list)
        or len(coeficientes) != len(datos["columnas_entrada"])
        or not all(_es_numero_finito(valor) for valor in coeficientes)
        or not _es_numero_finito(datos["termino_independiente"])
    ):
        raise ValueError("Los coeficientes del modelo no son válidos.")

    metricas = datos["metricas"]
    if not isinstance(metricas, dict) or set(metricas) != {"entrenamiento", "test"}:
        raise ValueError("Las métricas del modelo no son válidas.")
    for conjunto in metricas.values():
        if (
            not isinstance(conjunto, dict)
            or not isinstance(conjunto.get("filas"), int)
            or isinstance(conjunto.get("filas"), bool)
            or conjunto["filas"] < 0
            or not _es_numero_finito(conjunto.get("ecm"))
            or conjunto["ecm"] < 0
            or not _es_numero_finito(conjunto.get("r2"))
        ):
            raise ValueError("Las métricas del modelo no son válidas.")

    return {campo: datos[campo] for campo in CAMPOS}


def _es_numero_finito(valor: object) -> bool:
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        return False
    try:
        return math.isfinite(valor)
    except OverflowError:
        return False
