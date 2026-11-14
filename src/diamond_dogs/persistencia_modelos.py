import json
from pathlib import Path
import numpy as np

VERSION_FORMATO = 1

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
    ruta = Path(ruta)
    ruta.write_text(json.dumps(datos, indent=4, ensure_ascii=False), encoding="utf-8")
    return ruta