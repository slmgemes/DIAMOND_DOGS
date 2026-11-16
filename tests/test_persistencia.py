import json
from unittest.mock import patch
import numpy as np
import pandas as pd
import pytest
from diamond_dogs.crear_modelo import calcular_metricas, entrenar_modelo, escribir_formula
from diamond_dogs.persistencia_modelos import (EXTENSION, agregar_extension, construir_datos_modelo, existe_archivo, guardar_modelo)

ENTRADAS = ["edad", "habitaciones"]
SALIDA = "precio"

CAMPOS_ESPERADOS = {
    "version_formato", "descripcion", "columnas_entrada", "columna_salida",
    "coeficientes", "termino_independiente", "formula", "metricas",
}

@pytest.fixture
def modelo_entrenado():
    """Modelo entrenado como lo hace la aplicación (la salida es un DataFrame)."""
    x = pd.DataFrame({"edad": [1, 2, 3, 4, 5, 6, 7, 8],
                      "habitaciones": [3, 1, 4, 1, 5, 9, 2, 6]})
    y = pd.DataFrame({"precio": [10.0, 12.5, 17.0, 17.5, 23.0, 31.0, 19.0, 29.5]})
    x_train, x_test, y_train, y_test = x.iloc[:6], x.iloc[6:], y.iloc[:6], y.iloc[6:]

    modelo = entrenar_modelo(x_train, y_train)
    return {
        "modelo": modelo,
        "metricas": calcular_metricas(modelo, x_train, x_test, y_train, y_test),
        "formula": escribir_formula(SALIDA, ENTRADAS, modelo),
        "filas_train": len(x_train),
        "filas_test": len(x_test),
        "x_test": x_test,
    }

def guardar(ruta, m, descripcion=""):
    """Llama a guardar_modelo con los datos del modelo de prueba."""
    return guardar_modelo(
        ruta, m["modelo"], ENTRADAS, SALIDA, m["metricas"],
        m["filas_train"], m["filas_test"], m["formula"], descripcion,
    )


def test_agrega_extension_si_falta(tmp_path):
    """Comprueba que se añade .model.json cuando el usuario no la escribe."""
    assert agregar_extension(tmp_path / "modelo").name == "modelo" + EXTENSION

def test_no_duplica_la_extension(tmp_path):
    """Comprueba que no se añade otra vez si ya la lleva."""
    assert agregar_extension(tmp_path / "modelo.model.json").name == "modelo.model.json"

def test_json_se_convierte_en_model_json(tmp_path):
    """Comprueba que un nombre acabado en .json pasa a .model.json."""
    assert agregar_extension(tmp_path / "modelo.json").name == "modelo.model.json"

def test_nombre_vacio_da_error():
    """Comprueba que una ruta sin nombre de archivo lanza ValueError."""
    with pytest.raises(ValueError, match="vacío"):
        agregar_extension("")

def test_archivo_contiene_toda_la_informacion(tmp_path, modelo_entrenado):
    """Comprueba que el archivo guardado tiene todos los campos con sus valores."""
    m = modelo_entrenado
    ruta = guardar(tmp_path / "modelo", m, "Descripción de ejemplo")
    datos = json.loads(ruta.read_text(encoding="utf-8"))

    assert datos["descripcion"] == "Descripción de ejemplo"
    assert datos["columnas_entrada"] == ENTRADAS
    assert datos["columna_salida"] == SALIDA
    assert datos["coeficientes"] == pytest.approx(m["modelo"].coef_[0].tolist())
    assert datos["termino_independiente"] == pytest.approx(float(m["modelo"].intercept_[0]))
    assert datos["formula"] == m["formula"]

    entrenamiento = datos["metricas"]["entrenamiento"]
    test = datos["metricas"]["test"]
    assert entrenamiento["r2"] == pytest.approx(m["metricas"]["r2_train"])
    assert entrenamiento["ecm"] == pytest.approx(m["metricas"]["ecm_train"])
    assert test["r2"] == pytest.approx(m["metricas"]["r2_test"])
    assert test["ecm"] == pytest.approx(m["metricas"]["ecm_test"])

def test_archivo_no_contiene_datos_ni_graficos(tmp_path, modelo_entrenado):
    """Comprueba que solo se guardan los campos documentados."""
    ruta = guardar(tmp_path / "modelo", modelo_entrenado)
    datos = json.loads(ruta.read_text(encoding="utf-8"))

    assert set(datos) == CAMPOS_ESPERADOS
    assert set(datos["metricas"]) == {"entrenamiento", "test"}
    for bloque in datos["metricas"].values():
        assert set(bloque) == {"filas", "ecm", "r2"}
    # Un coeficiente por columna: nada que se parezca a filas del dataset.
    assert len(datos["coeficientes"]) == len(ENTRADAS)

def test_descripcion_vacia_se_guarda_vacia(tmp_path, modelo_entrenado):
    """Comprueba que sin descripción se guarda una cadena vacía (también con None)."""
    for descripcion, nombre in [("", "a"), (None, "b")]:
        ruta = guardar(tmp_path / nombre, modelo_entrenado, descripcion)
        assert json.loads(ruta.read_text(encoding="utf-8"))["descripcion"] == ""

def test_ruta_con_espacios_tildes_y_n(tmp_path, modelo_entrenado):
    """Comprueba que el guardado funciona en rutas con espacios, tildes y ñ."""
    carpeta = tmp_path / "carpeta con ñ y tildes áé"
    carpeta.mkdir()
    ruta = guardar(carpeta / "modelo año.model.json", modelo_entrenado, "Descripción con ñ y á")

    assert ruta.exists()
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert datos["descripcion"] == "Descripción con ñ y á"

def test_carpeta_inexistente_da_error_claro(tmp_path, modelo_entrenado):
    """Comprueba que una carpeta que no existe lanza ValueError con un mensaje claro."""
    with pytest.raises(ValueError, match="no existe"):
        guardar(tmp_path / "no_existe" / "modelo", modelo_entrenado)

def test_destino_no_valido_da_error_claro(tmp_path, modelo_entrenado):
    """Comprueba que no se puede guardar dentro de un archivo, y que el error es claro."""
    archivo = tmp_path / "archivo.txt"
    archivo.write_text("no soy una carpeta")
    with pytest.raises(ValueError):
        guardar(archivo / "modelo", modelo_entrenado)

def test_existe_archivo_usa_la_extension_añadida(tmp_path, modelo_entrenado):
    """Comprueba que se detecta el archivo existente aunque el usuario no escriba la extensión."""
    assert not existe_archivo(tmp_path / "modelo")
    guardar(tmp_path / "modelo", modelo_entrenado)
    assert existe_archivo(tmp_path / "modelo")
    assert existe_archivo(tmp_path / "modelo.model.json")

def test_sobrescribe_el_archivo_existente(tmp_path, modelo_entrenado):
    """Comprueba que al guardar de nuevo se sustituye el contenido."""
    guardar(tmp_path / "modelo", modelo_entrenado, "primera")
    ruta = guardar(tmp_path / "modelo", modelo_entrenado, "segunda")
    assert json.loads(ruta.read_text(encoding="utf-8"))["descripcion"] == "segunda"

def test_coeficientes_distintos_de_entradas_da_error(modelo_entrenado):
    """Comprueba que lanza ValueError si faltan columnas de entrada."""
    m = modelo_entrenado
    with pytest.raises(ValueError, match="coeficiente"):
        construir_datos_modelo(m["modelo"], ["edad"], SALIDA, m["metricas"],
                               m["filas_train"], m["filas_test"], m["formula"])

def test_con_el_archivo_se_pueden_hacer_predicciones(tmp_path, modelo_entrenado):
    """Comprueba que el archivo basta para predecir sin el dataset original."""
    m = modelo_entrenado
    ruta = guardar(tmp_path / "modelo", m)
    datos = json.loads(ruta.read_text(encoding="utf-8"))

    x = m["x_test"][datos["columnas_entrada"]].to_numpy()
    prediccion = x @ np.array(datos["coeficientes"]) + datos["termino_independiente"]
    esperada = m["modelo"].predict(m["x_test"]).ravel()
    assert np.allclose(prediccion, esperada)

def test_sin_permisos_da_error_claro(tmp_path, modelo_entrenado):
    """Comprueba que la falta de permisos lanza ValueError con un mensaje claro."""
    with patch("pathlib.Path.write_text", side_effect=PermissionError):
        with pytest.raises(ValueError, match="permisos"):
            guardar(tmp_path / "modelo", modelo_entrenado)

def test_otro_error_de_escritura_da_error_claro(tmp_path, modelo_entrenado):
    """Comprueba que cualquier otro fallo al escribir (por ejemplo, disco lleno) se avisa."""
    with patch("pathlib.Path.write_text", side_effect=OSError("disco lleno")):
        with pytest.raises(ValueError, match="No se pudo guardar"):
            guardar(tmp_path / "modelo", modelo_entrenado)