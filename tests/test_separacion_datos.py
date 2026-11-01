"""Pruebas unitarias de la función separar_datos."""

import pandas as pd
import pytest

from diamond_dogs.separacion_datos import separar_datos




def test_tamanos_segun_porcentaje():
    """Los tamaños de los conjuntos corresponden al porcentaje indicado."""
    df = pd.DataFrame({"edad": range(10), "precio": range(10)})

    # 20% de 10 filas: 2 de test y 8 de entrenamiento.
    x_train, x_test, y_train, y_test = separar_datos(df, ["edad"], "precio", 20)

    assert len(x_train) == 8
    assert len(y_train) == 8
    assert len(x_test) == 2
    assert len(y_test) == 2


def test_ninguna_fila_en_los_dos_conjuntos():
    """Ninguna fila aparece a la vez en entrenamiento y en test."""
    df = pd.DataFrame({"edad": range(10), "precio": range(10)})

    x_train, x_test, y_train, y_test = separar_datos(df, ["edad"], "precio", 20)

    # Entradas (x)
    assert set(x_train.index) & set(x_test.index) == set()          # ninguna repetida
    assert set(x_train.index) | set(x_test.index) == set(df.index)  # no se pierde ninguna

    # Salida (y)
    assert set(y_train.index) & set(y_test.index) == set()
    assert set(y_train.index) | set(y_test.index) == set(df.index)


def test_misma_semilla_misma_separacion():
    """La misma semilla produce la misma separación."""
    df = pd.DataFrame({"edad": range(10), "precio": range(10)})

    x_train_1, x_test_1, y_train_1, y_test_1 = separar_datos(
        df, ["edad"], "precio", 20, semilla=42
    )
    x_train_2, x_test_2, y_train_2, y_test_2 = separar_datos(
        df, ["edad"], "precio", 20, semilla=42
    )

    assert x_train_1.equals(x_train_2)
    assert x_test_1.equals(x_test_2)
    assert y_train_1.equals(y_train_2)
    assert y_test_1.equals(y_test_2)



def test_entradas_y_salida_emparejadas():
    """Cada fila de x conserva su valor de y, también con varias entradas."""
    df = pd.DataFrame({
        "edad": range(10),
        "peso": range(10),
        "precio": range(10),
    })

    x_train, x_test, y_train, y_test = separar_datos(
        df, ["edad", "peso"], "precio", 20
    )

    assert list(x_train.index) == list(y_train.index)
    assert list(x_test.index) == list(y_test.index)


def test_semilla_con_decimal_cero_es_valida():
    """Una semilla como 42.0 (como la devuelve ui.number) se acepta."""
    df = pd.DataFrame({"edad": range(10), "precio": range(10)})

    x_train, x_test, _, _ = separar_datos(df, ["edad"], "precio", 20, semilla=42.0)

    assert len(x_train) == 8
    assert len(x_test) == 2


# ---------- Manejo de errores ----------

def test_porcentaje_no_valido():
    """Un porcentaje fuera de 1-99 da error."""
    df = pd.DataFrame({"edad": range(10), "precio": range(10)})

    with pytest.raises(ValueError, match="entre 1 y 99"):
        separar_datos(df, ["edad"], "precio", 150)


def test_semilla_no_entera():
    """Una semilla con decimales da error."""
    df = pd.DataFrame({"edad": range(10), "precio": range(10)})

    with pytest.raises(ValueError, match="semilla"):
        separar_datos(df, ["edad"], "precio", 20, semilla=9.5)


def test_menos_de_5_filas():
    """Un dataset con menos de 5 filas da error."""
    df = pd.DataFrame({"edad": range(4), "precio": range(4)})

    with pytest.raises(ValueError, match="al menos 5"):
        separar_datos(df, ["edad"], "precio", 20)


def test_conjunto_vacio():
    """Si con el porcentaje elegido un conjunto quedaría vacío, da error."""
    # 5 filas y 81% de test: test = 5 filas, entrenamiento = 0.
    df = pd.DataFrame({"edad": range(5), "precio": range(5)})

    with pytest.raises(ValueError, match="quedaría vacío"):
        separar_datos(df, ["edad"], "precio", 81)