"""Pruebas unitarias del módulo prediccion."""

import pandas as pd
import pytest

from diamond_dogs.crear_modelo import (
    calcular_metricas,
    crear_datos_modelo,
    entrenar_modelo,
    escribir_formula,
)
from diamond_dogs.prediccion import prediccion


def crear_datos(x, y):
    """Entrena un modelo con x e y y devuelve sus DatosModelo, como hace la GUI."""
    modelo = entrenar_modelo(x, y)
    entradas = list(x.columns)
    salida = y.columns[0]
    formula = escribir_formula(salida, entradas, modelo)
    metricas = calcular_metricas(modelo, x, x, y, y)
    return crear_datos_modelo(modelo, entradas, salida, formula, metricas, x, x)


def test_prediccion_simple():
    """Con y = 2x + 5 y x = 3, la predicción es 2*3 + 5 = 11."""
    x = pd.DataFrame({"x": [1, 2, 3, 4]})
    y = pd.DataFrame({"y": 2 * x["x"] + 5})
    datos = crear_datos(x, y)

    assert prediccion(datos, ["3"]) == pytest.approx(11)


def test_prediccion_multiple():
    """Con y = 3a - 2b + 10, a = 4 y b = 1, la predicción es 12 - 2 + 10 = 20."""
    x = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [2, 1, 4, 3, 6]})
    y = pd.DataFrame({"y": 3 * x["a"] - 2 * x["b"] + 10})
    datos = crear_datos(x, y)

    assert prediccion(datos, ["4", "1"]) == pytest.approx(20)

 
def test_prediccion_con_coma_decimal():
    """'3,5' y '3.5' dan lo mismo: 2*3.5 + 5 = 12."""
    x = pd.DataFrame({"x": [1, 2, 3, 4]})
    y = pd.DataFrame({"y": 2 * x["x"] + 5})
    datos = crear_datos(x, y)

    assert prediccion(datos, ["3,5"]) == pytest.approx(12)
    assert prediccion(datos, ["3.5"]) == pytest.approx(12)


def test_prediccion_falta_un_valor():
    """Si un campo está vacío, el error dice qué variable falta."""
    x = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [2, 1, 4, 3, 6]})
    y = pd.DataFrame({"y": 3 * x["a"] - 2 * x["b"] + 10})
    datos = crear_datos(x, y)

    with pytest.raises(ValueError, match="Faltan valores para: b"):
        prediccion(datos, ["4", ""])


def test_prediccion_valor_no_numerico():
    """Si un valor no es un número, el error dice qué variable es."""
    x = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [2, 1, 4, 3, 6]})
    y = pd.DataFrame({"y": 3 * x["a"] - 2 * x["b"] + 10})
    datos = crear_datos(x, y)

    with pytest.raises(ValueError, match="Valor no numérico en: a"):
        prediccion(datos, ["hola", "1"])