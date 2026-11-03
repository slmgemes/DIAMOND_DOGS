import pytest
import pandas as pd
import numpy as np
from diamond_dogs.preprocesado import (
    identificar_nulos,
    eliminar_nulos,
    rellenar_media,
    rellenar_mediana,
    rellenar_constante
)

def test_constante_no_numerica():
    """Prueba que si el valor constante no es numérico, se lanza un ValueError."""
    x_train = pd.DataFrame({"entrada": [1.0, np.nan]})
    y_train = pd.Series([10, 20])
    x_test = pd.DataFrame({"entrada": [3.0]})
    y_test = pd.Series([30])

    with pytest.raises(ValueError, match="El valor constante no puede ser texto"):
        rellenar_constante(x_train, x_test, y_train, y_test, cte="abc")

    with pytest.raises(ValueError, match="Se requiere un valor constante"):
        rellenar_constante(x_train, x_test, y_train, y_test, cte="")

def test_eliminacion_deja_vacio():
    """Prueba que si eliminar nulos vacía el train o test, lanza un ValueError."""
    x_train = pd.DataFrame({"entrada 1": [np.nan, np.nan], "entrada 2": [1.0, np.nan]})
    y_train = pd.Series([10, 20], name="target")
    x_test = pd.DataFrame({"entrada 1": [1.0, 2.0], "entrada 2": [3.0, 4.0]})
    y_test = pd.Series([30, 40], name="target")

    with pytest.raises(ValueError, match="La eliminación de filas dejaría vacío"):
        eliminar_nulos(x_train, x_test, y_train, y_test)

def test_recuperacion_tras_error():
    """Prueba que tras un error o intento fallido, se puede cambiar de estrategia y aplicar otra con éxito."""
    x_train = pd.DataFrame({"entrada 1": [1.0, 2.0, np.nan], "entrada 2": [4.0, 5.0, 6.0]})
    y_train = pd.Series([10, 20, 30], name="target")
    x_test = pd.DataFrame({"entrada 1": [7.0, 8.0], "entrada 2": [9.0, np.nan]})
    y_test = pd.Series([40, 50], name="target")

    with pytest.raises(ValueError):
        rellenar_constante(x_train, x_test, y_train, y_test, cte="texto_invalido")

    x_train_resultado, x_test_resultado, _, _, resumen = rellenar_media(x_train, x_test, y_train, y_test)

    assert resumen["estrategia"] == "media"
    assert x_train_resultado.isnull().sum().sum() == 0
    assert x_test_resultado.isnull().sum().sum() == 0

def test_estrategia_eliminar_nulos():
    """Verifica que 'eliminar' borra correctamente las filas con valores NaN."""
    x_train = pd.DataFrame({"entrada 1": [1.0, 2.0, np.nan], "entrada 2": [4.0, 5.0, 6.0]})
    y_train = pd.Series([10, 20, 30], name="target")
    x_test = pd.DataFrame({"entrada 1": [7.0, 8.0], "entrada 2": [9.0, np.nan]})
    y_test = pd.Series([40, 50], name="target")

    x_train_resultado, x_test_resultado, _, _, resumen = eliminar_nulos(x_train, x_test, y_train, y_test)

    assert resumen["estrategia"] == "eliminar"
    assert resumen["filas_eliminadas_train"] == 1
    assert resumen["filas_eliminadas_test"] == 1
    assert len(x_train_resultado) == 2
    assert len(x_test_resultado) == 1
    assert x_train_resultado.isnull().sum().sum() == 0
    assert x_test_resultado.isnull().sum().sum() == 0

def test_estrategia_rellenar_media():
    """Verifica que 'media' rellena los NaN con el promedio de cada columna de train."""
    x_train = pd.DataFrame({"entrada": [2.0, 4.0, np.nan]})
    y_train = pd.Series([10, 20, 30], name="target")
    x_test = pd.DataFrame({"entrada": [np.nan, 8.0]})
    y_test = pd.Series([40, 50], name="target")

    x_train_resultado, x_test_resultado, _, _, resumen = rellenar_media(x_train, x_test, y_train, y_test)

    assert resumen["estrategia"] == "media"
    assert resumen["valores_rellenados_train"] == 1
    assert resumen["valores_rellenados_test"] == 1
    assert x_train_resultado.loc[2, "entrada"] == 3.0
    assert x_test_resultado.loc[0, "entrada"] == 3.0
    assert x_train_resultado.isnull().sum().sum() == 0
    assert x_test_resultado.isnull().sum().sum() == 0


def test_estrategia_rellenar_mediana():
    """Verifica que 'mediana' rellena los NaN con la mediana de cada columna de train."""
    x_train = pd.DataFrame({"entrada": [1.0, 5.0, 100.0, np.nan]})
    y_train = pd.Series([10, 20, 30, 40], name="target")
    x_test = pd.DataFrame({"entrada": [np.nan, 2.0]})
    y_test = pd.Series([50, 60], name="target")

    x_train_resultado, x_test_resultado, _, _, resumen = rellenar_mediana(x_train, x_test, y_train, y_test)

    assert resumen["estrategia"] == "mediana"
    assert resumen["valores_rellenados_train"] == 1
    assert resumen["valores_rellenados_test"] == 1
    assert x_train_resultado.loc[3, "entrada"] == 5.0
    assert x_test_resultado.loc[0, "entrada"] == 5.0
    assert x_train_resultado.isnull().sum().sum() == 0
    assert x_test_resultado.isnull().sum().sum() == 0


def test_estrategia_rellenar_constante():
    """Verifica que 'constante' sustituye todos los NaN por el valor numérico indicado."""
    x_train = pd.DataFrame({"entrada 1": [1.0, np.nan], "entrada 2": [np.nan, 4.0]})
    y_train = pd.Series([10, 20], name="target")
    x_test = pd.DataFrame({"entrada 1": [np.nan], "entrada 2": [5.0]})
    y_test = pd.Series([30], name="target")

    valor_cte = -99.0

    x_train_resultado, x_test_resultado, _, _, resumen = rellenar_constante(
        x_train, x_test, y_train, y_test, cte=valor_cte
    )

    assert resumen["estrategia"] == "constante"
    assert resumen["valores_rellenados_train"] == 2
    assert resumen["valores_rellenados_test"] == 1
    assert x_train_resultado.loc[1, "entrada 1"] == valor_cte
    assert x_train_resultado.loc[0, "entrada 2"] == valor_cte
    assert x_test_resultado.loc[0, "entrada 1"] == valor_cte
    assert x_train_resultado.isnull().sum().sum() == 0
    assert x_test_resultado.isnull().sum().sum() == 0