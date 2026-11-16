"""Lógica del modelo de regresión lineal: entrenar, métricas y fórmula."""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
from typing import TypedDict


class MetricasPersistidas(TypedDict):
    """Métricas de un subconjunto dentro de la estructura de persistencia."""

    filas: int
    ecm: float
    r2: float


class DatosModelo(TypedDict):
    """Información del modelo con los campos de la estructura JSON investigada."""

    version_formato: int
    descripcion: str
    columnas_entrada: list[str]
    columna_salida: str
    coeficientes: list[float]
    termino_independiente: float
    formula: str
    metricas: dict[str, MetricasPersistidas]


def crear_datos_modelo(
    modelo: LinearRegression,
    entradas: list[str],
    salida: str,
    formula: str,
    metricas: dict[str, float],
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
) -> DatosModelo:
    """Construye la información del modelo con la estructura del prototipo JSON.

    La descripción se inicia vacía para que cada modelo nuevo tenga su propio
    valor, independiente del componente de interfaz.
    """
    return {
        "version_formato": 1,
        "descripcion": "",
        "columnas_entrada": list(entradas),
        "columna_salida": salida,
        "coeficientes": [float(coeficiente) for coeficiente in modelo.coef_[0]],
        "termino_independiente": float(modelo.intercept_[0]),
        "formula": formula,
        "metricas": {
            "entrenamiento": {
                "filas": len(x_train),
                "ecm": float(metricas["ecm_train"]),
                "r2": float(metricas["r2_train"]),
            },
            "test": {
                "filas": len(x_test),
                "ecm": float(metricas["ecm_test"]),
                "r2": float(metricas["r2_test"]),
            },
        },
    }


def actualizar_descripcion(datos_modelo: DatosModelo, descripcion: str) -> None:
    """Actualiza la descripción guardada en la información del modelo."""
    datos_modelo["descripcion"] = descripcion

def entrenar_modelo(x_train, y_train):
    """Entrena un modelo de regresión lineal solo con el conjunto de entrenamiento.

    Parameters
    ----------
    x_train : pd.DataFrame
        Columnas de entrada del conjunto de entrenamiento.
    y_train : pd.DataFrame
        Columna de salida del conjunto de entrenamiento.

    Returns
    -------
    LinearRegression
        Modelo entrenado.
    """
    modelo = LinearRegression()
    modelo.fit(x_train, y_train)
    return modelo


def calcular_metricas(modelo:LinearRegression, x_train, x_test, y_train, y_test):
    """Calcula el R² y el ECM en entrenamiento y en test.

    Parameters
    ----------
    modelo : LinearRegression
        Modelo entrenado.
    x_train, x_test : pd.DataFrame
        Columnas de entrada de entrenamiento y de test.
    y_train, y_test : pd.DataFrame
        Columna de salida de entrenamiento y de test.

    Returns
    -------
    dict
        Claves "r2_train", "r2_test", "ecm_train" y "ecm_test".
    """

    
    prediccion_train = modelo.predict(x_train)
    prediccion_test = modelo.predict(x_test)

    return {
        "r2_train": r2_score(y_train, prediccion_train),
        "r2_test": r2_score(y_test, prediccion_test),
        "ecm_train": mean_squared_error(y_train, prediccion_train),
        "ecm_test": mean_squared_error(y_test, prediccion_test),
    }


def escribir_formula(salida, entradas, modelo:LinearRegression):
    """Escribe la fórmula del modelo con los nombres de las columnas.

    Los números se muestran siempre con 4 decimales, y los negativos restando.

    Parameters
    ----------
    salida : str
        Nombre de la columna de salida.
    entradas : list of str
        Nombres de las columnas de entrada.
    modelo : LinearRegression
        Modelo entrenado, con la salida como DataFrame.

    Returns
    -------
    str
        Fórmula, por ejemplo "precio = 4.20 * edad - 15.30".
    """


    # Como y es un DataFrame, coef_ es [[c1, c2, ...]] e intercept_ es [t].
    coeficientes = modelo.coef_[0]
    termino = modelo.intercept_[0]

    formula = f"{salida} ="

    # Un trozo por cada columna de entrada.
    for i in range(len(entradas)):
        coef = coeficientes[i]
        if i == 0:
            formula += f" {coef:.4f} * {entradas[i]}"
        elif coef < 0:
            formula += f" - {abs(coef):.4f} * {entradas[i]}"
        else:
            formula += f" + {coef:.4f} * {entradas[i]}"

    # Al final, el término independiente con su signo.
    if termino < 0:
        formula += f" - {abs(termino):.4f}"
    else:
        formula += f" + {termino:.4f}"

    return formula

def datos_grafico(modelo, x_train, x_test, y_train, y_test):
    """Prepara los datos del gráfico del ajuste.

    - Regresión simple (una entrada): eje x = entrada, eje y = salida real,
      y la recta del modelo.
    - Regresión múltiple: eje x = valor real, eje y = valor predicho,
      y la diagonal donde real y predicho coinciden.

    Parameters
    ----------
    modelo : LinearRegression
        Modelo entrenado.
    x_train, x_test : pd.DataFrame
        Columnas de entrada de entrenamiento y de test.
    y_train, y_test : pd.DataFrame
        Columna de salida de entrenamiento y de test.

    Returns
    -------
    dict
        Puntos de train y test, línea y nombres de los ejes.
    """
    if len(x_train.columns) == 1:
        # Simple: las predicciones caen todas sobre la recta del modelo.
        return {
            "x_train": x_train, "y_train": y_train,
            "x_test": x_test, "y_test": y_test,
            "linea_x": x_train, "linea_y": modelo.predict(x_train),
            "eje_x": x_train.columns[0], "eje_y": y_train.columns[0],
            "nombre_linea": "Recta del modelo",
        }

    # Múltiple: los puntos (real, real) caen todos sobre la diagonal.
    return {
        "x_train": y_train, "y_train": modelo.predict(x_train),
        "x_test": y_test, "y_test": modelo.predict(x_test),
        "linea_x": y_train, "linea_y": y_train,
        "eje_x": "Valor real", "eje_y": "Valor predicho",
        "nombre_linea": "Valor real = valor predicho",
    }