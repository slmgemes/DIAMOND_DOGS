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
def test_identificar_nulos():
    """Verifica que identificar_nulos detecta correctamente los NaN y devuelve 
    los contadores y desgloses esperados."""
    x_train = pd.DataFrame({"entrada": [1.0, np.nan]})
    y_train = pd.Series([10, 20], name="target")
    x_test = pd.DataFrame({"entrada": [3.0]})
    y_test = pd.Series([30], name="target")

    resultado = identificar_nulos(x_train, x_test, y_train, y_test)

    assert resultado["nulos"] is True
    assert resultado["nulos_x_train"]["entrada"] == 1

def test_identificar_nulos_sin_nulos():
    x_train = pd.DataFrame({"entrada": [1.0, 2.0]})
    y_train = pd.Series([10, 20], name="target")
    x_test = pd.DataFrame({"entrada": [3.0]})
    y_test = pd.Series([30], name="target")

    resultado = identificar_nulos(x_train, x_test, y_train, y_test)

    assert resultado["nulos"] is False
    assert "No se han detectado valores inexistentes" in resultado["mensaje"]

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

def test_eliminar_nulos_con_dataframe_en_y():
    """Verifica que eliminar_nulos funciona correctamente cuando y es un DataFrame (cubriendo la rama else)."""
    x_train = pd.DataFrame({"entrada": [1.0, np.nan]})
    y_train = pd.DataFrame({"target": [10.0, 20.0]})
    x_test = pd.DataFrame({"entrada": [3.0]})
    y_test = pd.DataFrame({"target": [30.0]})

    x_tr_res, _, y_tr_res, _, resumen = eliminar_nulos(x_train, x_test, y_train, y_test)
    
    assert resumen["estrategia"] == "eliminar"
    assert isinstance(y_tr_res, pd.DataFrame)
    assert len(x_tr_res) == 1

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

def test_rellenar_constante_con_dataframe_en_y():
    """Verifica que rellenar_constante funciona correctamente cuando y es un DataFrame (cubriendo la rama else)."""
    x_train = pd.DataFrame({"entrada": [1.0, np.nan]})
    y_train = pd.DataFrame({"target": [10.0, np.nan]})
    x_test = pd.DataFrame({"entrada": [3.0]})
    y_test = pd.DataFrame({"target": [30.0]})

    _, _, y_tr_res, _, resumen = rellenar_constante(
        x_train, x_test, y_train, y_test, cte=5.0
    )
    
    assert resumen["estrategia"] == "constante"
    assert isinstance(y_tr_res, pd.DataFrame)
    assert y_tr_res.loc[1, "target"] == 5.0

def test_cambio_estrategia_sobre_datos_originales():
    """Verifica que al cambiar de estrategia, esta se aplica sobre los datos 
    originales guardados en la base y no sobre el resultado de una estrategia previa."""
    
    x_train = pd.DataFrame({"entrada": [2.0, 4.0, np.nan]})
    y_train = pd.Series([10, 20, 30], name="target")
    x_test = pd.DataFrame({"entrada": [8.0]})
    y_test = pd.Series([40], name="target")

    x_train_base = x_train.copy()
    x_test_base = x_test.copy()
    y_train_base = y_train.copy()
    y_test_base = y_test.copy()

    xt_1, _, _, _, _ = rellenar_constante(
        x_train_base, x_test_base, y_train_base, y_test_base, cte=-99.0
    )
    assert xt_1.loc[2, "entrada"] == -99.0

    xt_2, _, _, _, resumen_2 = rellenar_media(
        x_train_base, x_test_base, y_train_base, y_test_base
    )

    assert resumen_2["estrategia"] == "media"
    assert xt_2.loc[2, "entrada"] == 3.0