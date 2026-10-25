import pandas as pd
import pytest

from diamond_dogs.seleccion import validar_seleccion


@pytest.fixture
def df():
    return pd.DataFrame({
        "a": [1, 2, 3],
        "b": [0.5, 1.5, 2.5],
        "y": [10, 20, 30],
        "texto": ["x", "y", "z"],  # columna no numérica
    })


def test_seleccion_valida(df):
    assert validar_seleccion(df, ["a", "b"], "y") == []


def test_sin_features(df):
    errores = validar_seleccion(df, [], "y")
    assert len(errores) == 1 and "entrada" in errores[0]


def test_sin_target(df):
    errores = validar_seleccion(df, ["a"], None)
    assert len(errores) == 1 and "salida" in errores[0]


def test_falta_todo(df):
    assert len(validar_seleccion(df, [], None)) == 2


def test_target_tambien_entrada(df):
    errores = validar_seleccion(df, ["a", "y"], "y")
    assert any("entrada y salida" in e for e in errores)


def test_columna_inexistente(df):
    errores = validar_seleccion(df, ["a", "zzz"], "y")
    assert any("zzz" in e for e in errores)


def test_feature_no_numerica(df):
    errores = validar_seleccion(df, ["a", "texto"], "y")
    assert any("texto" in e for e in errores)


def test_target_no_numerico(df):
    errores = validar_seleccion(df, ["a"], "texto")
    assert any("texto" in e for e in errores)


def test_regresion_simple_rechaza_varias(df):
    errores = validar_seleccion(df, ["a", "b"], "y", multiple=False)
    assert any("simple" in e for e in errores)


def test_regresion_simple_acepta_una(df):
    assert validar_seleccion(df, ["a"], "y", multiple=False) == []