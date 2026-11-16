import json
from unittest.mock import patch
import numpy as np
import pandas as pd
import pytest
from diamond_dogs.crear_modelo import (
    actualizar_descripcion, calcular_metricas, crear_datos_modelo,
    entrenar_modelo, escribir_formula,
)
from diamond_dogs.persistencia_modelos import (EXTENSION, agregar_extension, existe_archivo, guardar_modelo)

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
    metricas = calcular_metricas(modelo, x_train, x_test, y_train, y_test)
    formula = escribir_formula(SALIDA, ENTRADAS, modelo)
    return {
        "modelo": modelo,
        "x_test": x_test,
        "datos": crear_datos_modelo(modelo, ENTRADAS, SALIDA, formula, metricas, x_train, x_test),
    }


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
    actualizar_descripcion(m["datos"], "Descripción de ejemplo")
    ruta = guardar_modelo(tmp_path / "modelo", m["datos"])
    guardado = json.loads(ruta.read_text(encoding="utf-8"))

    assert guardado == m["datos"]
    assert guardado["descripcion"] == "Descripción de ejemplo"
    assert guardado["columnas_entrada"] == ENTRADAS
    assert guardado["columna_salida"] == SALIDA
    assert guardado["coeficientes"] == pytest.approx(m["modelo"].coef_[0].tolist())
    assert guardado["termino_independiente"] == pytest.approx(float(m["modelo"].intercept_[0]))
    assert set(guardado["metricas"]) == {"entrenamiento", "test"}

def test_archivo_no_contiene_datos_ni_graficos(tmp_path, modelo_entrenado):
    """Comprueba que solo se guardan los campos documentados, aunque haya más."""
    datos = {**modelo_entrenado["datos"], "x_train": [[1, 3], [2, 1]], "grafico": "<svg></svg>"}
    ruta = guardar_modelo(tmp_path / "modelo", datos)
    guardado = json.loads(ruta.read_text(encoding="utf-8"))

    assert set(guardado) == CAMPOS_ESPERADOS
    for bloque in guardado["metricas"].values():
        assert set(bloque) == {"filas", "ecm", "r2"}
    assert len(guardado["coeficientes"]) == len(ENTRADAS)

def test_descripcion_vacia_se_guarda_vacia(tmp_path, modelo_entrenado):
    """Comprueba que un modelo nuevo, sin descripción, se guarda con una cadena vacía."""
    ruta = guardar_modelo(tmp_path / "modelo", modelo_entrenado["datos"])
    assert json.loads(ruta.read_text(encoding="utf-8"))["descripcion"] == ""

def test_ruta_con_espacios_tildes_y_n(tmp_path, modelo_entrenado):
    """Comprueba que el guardado funciona en rutas con espacios, tildes y ñ."""
    datos = modelo_entrenado["datos"]
    actualizar_descripcion(datos, "Descripción con ñ y á")
    carpeta = tmp_path / "carpeta con ñ y tildes áé"
    carpeta.mkdir()
    ruta = guardar_modelo(carpeta / "modelo año.model.json", datos)

    assert ruta.exists()
    assert json.loads(ruta.read_text(encoding="utf-8"))["descripcion"] == "Descripción con ñ y á"

def test_faltan_campos_da_error_y_no_crea_el_archivo(tmp_path, modelo_entrenado):
    """Comprueba que lanza ValueError si falta algún campo, sin crear el archivo."""
    datos = dict(modelo_entrenado["datos"])
    del datos["formula"]
    with pytest.raises(ValueError, match="formula"):
        guardar_modelo(tmp_path / "modelo", datos)
    assert not (tmp_path / "modelo.model.json").exists()

def test_carpeta_inexistente_da_error_claro(tmp_path, modelo_entrenado):
    """Comprueba que una carpeta que no existe lanza ValueError con un mensaje claro."""
    with pytest.raises(ValueError, match="no existe"):
        guardar_modelo(tmp_path / "no_existe" / "modelo", modelo_entrenado["datos"])

def test_destino_no_valido_da_error_claro(tmp_path, modelo_entrenado):
    """Comprueba que no se puede guardar dentro de un archivo, y que el error es claro."""
    archivo = tmp_path / "archivo.txt"
    archivo.write_text("no soy una carpeta")
    with pytest.raises(ValueError):
        guardar_modelo(archivo / "modelo", modelo_entrenado["datos"])

def test_existe_archivo_usa_la_extension_añadida(tmp_path, modelo_entrenado):
    """Comprueba que se detecta el archivo existente aunque el usuario no escriba la extensión."""
    assert not existe_archivo(tmp_path / "modelo")
    guardar_modelo(tmp_path / "modelo", modelo_entrenado["datos"])
    assert existe_archivo(tmp_path / "modelo")
    assert existe_archivo(tmp_path / "modelo.model.json")

def test_sobrescribe_el_archivo_existente(tmp_path, modelo_entrenado):
    """Comprueba que al guardar de nuevo se sustituye el contenido."""
    datos = modelo_entrenado["datos"]
    actualizar_descripcion(datos, "primera")
    guardar_modelo(tmp_path / "modelo", datos)
    actualizar_descripcion(datos, "segunda")
    ruta = guardar_modelo(tmp_path / "modelo", datos)
    assert json.loads(ruta.read_text(encoding="utf-8"))["descripcion"] == "segunda"

def test_con_el_archivo_se_pueden_hacer_predicciones(tmp_path, modelo_entrenado):
    """Comprueba que el archivo basta para predecir sin el dataset original."""
    m = modelo_entrenado
    ruta = guardar_modelo(tmp_path / "modelo", m["datos"])
    guardado = json.loads(ruta.read_text(encoding="utf-8"))

    x = m["x_test"][guardado["columnas_entrada"]].to_numpy()
    prediccion = x @ np.array(guardado["coeficientes"]) + guardado["termino_independiente"]
    esperada = m["modelo"].predict(m["x_test"]).ravel()
    assert np.allclose(prediccion, esperada)

def test_sin_permisos_da_error_claro(tmp_path, modelo_entrenado):
    """Comprueba que la falta de permisos lanza ValueError con un mensaje claro."""
    with patch("pathlib.Path.write_text", side_effect=PermissionError):
        with pytest.raises(ValueError, match="permisos"):
            guardar_modelo(tmp_path / "modelo", modelo_entrenado["datos"])

def test_otro_error_de_escritura_da_error_claro(tmp_path, modelo_entrenado):
    """Comprueba que cualquier otro fallo al escribir (por ejemplo, disco lleno) se avisa."""
    with patch("pathlib.Path.write_text", side_effect=OSError("disco lleno")):
        with pytest.raises(ValueError, match="No se pudo guardar"):
            guardar_modelo(tmp_path / "modelo", modelo_entrenado["datos"])