import json
import time

import numpy as np
import pandas as pd

from diamond_dogs.tabla_datos import preparar_tabla


def test_la_tabla_conserva_todas_las_filas_de_un_dataset_grande():
    """Con decenas de miles de filas no se pierde ninguna y el orden se mantiene."""
    filas = 25_000
    df = pd.DataFrame({"id": np.arange(filas), "valor": np.arange(filas) * 0.5})

    datos = preparar_tabla(df)

    assert len(datos["rowData"]) == filas
    assert datos["rowData"][0] == {"c0": 0, "c1": 0.0}
    assert datos["rowData"][-1] == {"c0": filas - 1, "c1": (filas - 1) * 0.5}


def test_preparar_un_dataset_grande_es_rapido():
    """Preparar 25.000 filas y 10 columnas tarda segundos como mucho."""
    df = pd.DataFrame(np.random.default_rng(0).random((25_000, 10)),
                      columns=[f"col{i}" for i in range(10)])

    inicio = time.perf_counter()
    preparar_tabla(df)

    assert time.perf_counter() - inicio < 5


def test_las_columnas_numericas_se_mantienen_como_numeros():
    """Los números siguen siendo números (se ordenan bien) y la columna lo indica."""
    df = pd.DataFrame({"edad": [10, 9, 100], "nombre": ["a", "b", "c"]})

    datos = preparar_tabla(df)

    assert datos["columnDefs"][0] == {"field": "c0", "headerName": "edad", "type": "numericColumn"}
    assert "type" not in datos["columnDefs"][1]
    assert [fila["c0"] for fila in datos["rowData"]] == [10, 9, 100]
    assert [fila["c1"] for fila in datos["rowData"]] == ["a", "b", "c"]


def test_los_valores_inexistentes_se_dejan_en_blanco():
    """Un valor inexistente es None en una columna numérica y vacío en una de texto."""
    df = pd.DataFrame({"n": [1.0, np.nan], "t": ["x", None]})

    datos = preparar_tabla(df)

    assert datos["rowData"][1] == {"c0": None, "c1": ""}


def test_los_datos_se_pueden_enviar_a_la_tabla_como_json():
    """Todo el resultado se puede convertir a JSON, incluidos fechas y booleanos."""
    df = pd.DataFrame({
        "n": [1, 2],
        "fecha": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "ok": [True, False],
    })

    datos = preparar_tabla(df)

    assert json.loads(json.dumps(datos)) == datos


def test_nombres_de_columna_con_puntos_o_repetidos():
    """Los campos se numeran, así que los nombres raros no se mezclan ni se pierden."""
    df = pd.DataFrame([[1, 2, 3]], columns=["total.rooms", "x", "x"])

    datos = preparar_tabla(df)

    assert [c["headerName"] for c in datos["columnDefs"]] == ["total.rooms", "x", "x"]
    assert datos["rowData"][0] == {"c0": 1, "c1": 2, "c2": 3}
