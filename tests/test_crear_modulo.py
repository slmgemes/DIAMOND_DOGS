"""Pruebas unitarias del módulo crear_modelo."""
 
import pandas as pd
import pytest
 
from diamond_dogs.crear_modelo import (
    calcular_metricas,
    datos_grafico,
    entrenar_modelo,
    escribir_formula,
)
 
 
# ---------- Entrenar ----------
 
def test_entrenar_modelo_aprende_la_recta():
    """Con datos que siguen y = 2x + 5, el modelo aprende 2 y 5."""
    x = pd.DataFrame({"x": [1, 2, 3, 4]})
    y = pd.DataFrame({"y": [7, 9, 11, 13]})
 
    modelo = entrenar_modelo(x, y)
 
    assert modelo.coef_[0][0] == pytest.approx(2)
    assert modelo.intercept_[0] == pytest.approx(5)
 
 
# ---------- Métricas ----------
 
def test_metricas_devuelve_las_cuatro():
    """Devuelve el R² y el ECM de entrenamiento y de test."""
    x_train = pd.DataFrame({"x": [1, 2, 3]})
    y_train = pd.DataFrame({"y": [1, 2, 3]})
    x_test = pd.DataFrame({"x": [4, 5]})
    y_test = pd.DataFrame({"y": [4, 5]})
    modelo = entrenar_modelo(x_train, y_train)
 
    metricas = calcular_metricas(modelo, x_train, x_test, y_train, y_test)
 
    assert set(metricas) == {"r2_train", "r2_test", "ecm_train", "ecm_test"}
 
 
def test_metricas_modelo_perfecto():
    """Si el modelo acierta todo: R² = 1 y ECM = 0."""
    x_train = pd.DataFrame({"x": [1, 2, 3]})
    y_train = pd.DataFrame({"y": [1, 2, 3]})
    x_test = pd.DataFrame({"x": [4, 5]})
    y_test = pd.DataFrame({"y": [4, 5]})
    modelo = entrenar_modelo(x_train, y_train)
 
    metricas = calcular_metricas(modelo, x_train, x_test, y_train, y_test)
 
    assert metricas["r2_train"] == pytest.approx(1)
    assert metricas["r2_test"] == pytest.approx(1)
    assert metricas["ecm_train"] == pytest.approx(0)
    assert metricas["ecm_test"] == pytest.approx(0)
 
 
def test_metricas_valores_conocidos_en_test():
    """Con errores conocidos en test, el ECM y el R² son los esperados."""
    # El modelo aprende y = x.
    x_train = pd.DataFrame({"x": [1, 2, 3]})
    y_train = pd.DataFrame({"y": [1, 2, 3]})
    # En test predice 4 y 5, pero los reales son 5 y 4: errores de 1 y -1.
    x_test = pd.DataFrame({"x": [4, 5]})
    y_test = pd.DataFrame({"y": [5, 4]})
    modelo = entrenar_modelo(x_train, y_train)
 
    metricas = calcular_metricas(modelo, x_train, x_test, y_train, y_test)
 
    # ECM = (1² + 1²) / 2 = 1
    assert metricas["ecm_test"] == pytest.approx(1)
    # R² = 1 - 2 / 0.5 = -3 (peor que decir siempre la media)
    assert metricas["r2_test"] == pytest.approx(-3)
 
 
# ---------- Fórmula ----------
 
def test_formula_con_coeficiente_negativo():
    """Un coeficiente negativo se muestra restando, sin '+ -'."""
    # y = 3*a - 2*b + 10
    x = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [2, 1, 4, 3, 6]})
    y = pd.DataFrame({"y": 3 * x["a"] - 2 * x["b"] + 10})
    modelo = entrenar_modelo(x, y)
 
    formula = escribir_formula("y", ["a", "b"], modelo)
 
    assert formula == "y = 3.0000 * a - 2.0000 * b + 10.0000"
    assert "+ -" not in formula
 
 
def test_formula_con_termino_negativo():
    """Un término independiente negativo también se muestra restando."""
    # y = 2*x - 7
    x = pd.DataFrame({"x": [1, 2, 3, 4]})
    y = pd.DataFrame({"y": 2 * x["x"] - 7})
    modelo = entrenar_modelo(x, y)
 
    formula = escribir_formula("y", ["x"], modelo)
 
    assert formula == "y = 2.0000 * x - 7.0000"
 
 
def test_formula_con_primer_coeficiente_negativo():
    """Si el primer coeficiente es negativo, sale con su signo delante."""
    # y = -4*x + 1
    x = pd.DataFrame({"x": [1, 2, 3, 4]})
    y = pd.DataFrame({"y": -4 * x["x"] + 1})
    modelo = entrenar_modelo(x, y)
 
    formula = escribir_formula("y", ["x"], modelo)
 
    assert formula == "y = -4.0000 * x + 1.0000"
 
 
# ---------- Datos del gráfico ----------
 
def test_datos_grafico_simple():
    """Con una entrada: ejes con los nombres de las columnas y la recta del modelo."""
    # y = 2x + 5
    x_train = pd.DataFrame({"x": [1, 2, 3]})
    y_train = pd.DataFrame({"y": [7, 9, 11]})
    x_test = pd.DataFrame({"x": [4]})
    y_test = pd.DataFrame({"y": [13]})
    modelo = entrenar_modelo(x_train, y_train)
 
    datos = datos_grafico(modelo, x_train, x_test, y_train, y_test)
 
    assert datos["eje_x"] == "x"
    assert datos["eje_y"] == "y"
    assert datos["x_train"].equals(x_train)
    assert datos["y_test"].equals(y_test)
    # La línea son las predicciones: caen sobre y = 2x + 5.
    assert [fila[0] for fila in datos["linea_y"]] == pytest.approx([7, 9, 11])
 
 
def test_datos_grafico_multiple():
    """Con varias entradas: real frente a predicho y la diagonal real = predicho."""
    x_train = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 4, 3]})
    y_train = pd.DataFrame({"y": [5, 4, 11, 10]})
    x_test = pd.DataFrame({"a": [5], "b": [6]})
    y_test = pd.DataFrame({"y": [16]})
    modelo = entrenar_modelo(x_train, y_train)
 
    datos = datos_grafico(modelo, x_train, x_test, y_train, y_test)
 
    assert datos["eje_x"] == "Valor real"
    assert datos["eje_y"] == "Valor predicho"
    assert datos["x_train"].equals(y_train)                 # eje x: valores reales
    assert datos["linea_x"].equals(datos["linea_y"])        # diagonal: x = y