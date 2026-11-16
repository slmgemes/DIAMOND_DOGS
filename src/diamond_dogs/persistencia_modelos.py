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

def construir_datos_modelo(modelo, entradas, salida, metricas, filas_train, filas_test, formula, descripcion=""):
    coeficientes = np.ravel(modelo.coef_).tolist()
    if len(coeficientes) != len(entradas):
        raise ValueError("El modelo debe tener un coeficiente por cada columna de entrada.")

    return {
        "version_formato": VERSION_FORMATO,
        "descripcion": descripcion or "",
        "columnas_entrada": list(entradas),
        "columna_salida": salida,
        "coeficientes": coeficientes,
        "termino_independiente": float(np.ravel(modelo.intercept_)[0]),
        "formula": formula,
        "metricas": {
            "entrenamiento": {
                "filas": int(filas_train),
                "ecm": float(metricas["ecm_train"]),
                "r2": float(metricas["r2_train"]),
            },
            "test": {
                "filas": int(filas_test),
                "ecm": float(metricas["ecm_test"]),
                "r2": float(metricas["r2_test"]),
            },
        },
    }

def guardar_modelo(ruta, modelo, entradas, salida, metricas, filas_train, filas_test, formula, descripcion=""):
    datos = construir_datos_modelo(
        modelo, entradas, salida, metricas, filas_train, filas_test, formula, descripcion
    )
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
