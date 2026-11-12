import json
from pathlib import Path
import tempfile

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from diamond_dogs.importador import ImportadorDatos
from diamond_dogs.preprocesado import eliminar_nulos
from diamond_dogs.separacion_datos import separar_datos

from prueba_regresion import (
    ARCHIVO, ENTRADAS, SALIDA, PORCENTAJE_TEST, SEMILLA, VALOR_NUEVO,
    escribir_formula)

CAMPOS = ["version_formato", "descripcion", "columnas_entrada", "columna_salida",
          "coeficientes", "termino_independiente", "formula", "metricas"]

#Crear el modelo
def cargar_y_preparar_datos(archivo, entradas, salida, porcentaje_test, semilla):
    """Carga el dataset, separa en train/test y elimina nulos."""
    df, _ = ImportadorDatos(archivo).importar()
    x_train, x_test, y_train, y_test = separar_datos(
        df, entradas, salida, porcentaje_test, semilla=semilla
    )
    x_train, x_test, y_train, y_test, resumen = eliminar_nulos(
        x_train, x_test, y_train, y_test
    )
    return x_train, x_test, y_train, y_test, resumen

def entrenar_modelo(x_train, y_train):
    """Entrena y devuelve un modelo de regresión lineal."""
    modelo = LinearRegression()
    modelo.fit(x_train, y_train)
    return modelo

def calcular_metricas_y_parametros(modelo, x_train, x_test, y_train, y_test, salida, entradas):
    """Calcula métricas, coeficientes, término independiente y fórmula."""
    pred_train = modelo.predict(x_train)
    pred_test = modelo.predict(x_test)
 
    ecm_train = float(mean_squared_error(y_train, pred_train))
    ecm_test = float(mean_squared_error(y_test, pred_test))
    r2_tr = float(r2_score(y_train, pred_train))
    r2_te = float(r2_score(y_test, pred_test))
 
    coeficientes = modelo.coef_[0].tolist()
    termino = float(modelo.intercept_[0])
    formula = escribir_formula(salida, entradas, coeficientes, termino)

    return {
        "coeficientes": coeficientes,
        "termino_independiente": termino,
        "formula": formula,
        "metricas": {
            "entrenamiento": {
                "filas": len(x_train),
                "ecm": ecm_train,
                "r2": r2_tr
            },
            "test": {
                "filas": len(x_test),
                "ecm": ecm_test,
                "r2": r2_te
            }
        }
    }


#Guardar el modelo
def guardar_modelo_json(ruta, datos):
    """Guarda el diccionario de datos del modelo en un archivo JSON."""
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


def cargar_modelo_json(ruta):
    """Carga y devuelve el diccionario desde el archivo JSON, comprobando que es válido."""
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)
 
    faltan = [c for c in CAMPOS if c not in datos]
    if faltan:
        raise ValueError(f"Archivo de modelo no válido, faltan: {faltan}")
    coeficientes = datos["coeficientes"]
    if not all(isinstance(c, (int, float)) for c in coeficientes):
        raise ValueError("Los coeficientes deben ser números.")
    if len(coeficientes) != len(datos["columnas_entrada"]):
        raise ValueError("Debe haber un coeficiente por cada columna de entrada.")
    return datos

def reconstruir_modelo(datos_cargados):
    """Reconstruye un objeto LinearRegression a partir de los datos cargados."""
    modelo = LinearRegression()
    modelo.coef_ = np.array([datos_cargados["coeficientes"]])
    modelo.intercept_ = np.array([datos_cargados["termino_independiente"]])
    modelo.n_features_in_ = len(datos_cargados["coeficientes"])
    modelo.feature_names_in_ = np.array(datos_cargados["columnas_entrada"], dtype=object)
    return modelo


def main():
    """Coordina todo el flujo usando una carpeta temporal (sin dejar archivos reales)."""
    print("--- 1. ENTRENAMIENTO DEL MODELO ORIGINAL ---")
    x_train, x_test, y_train, y_test, _ = cargar_y_preparar_datos(
        ARCHIVO, ENTRADAS, SALIDA, PORCENTAJE_TEST, SEMILLA
    )
    print(f"Datos preparados: {len(x_train)} train, {len(x_test)} test (Nulos eliminados)")
 
    modelo_original = entrenar_modelo(x_train, y_train)
    info_modelo = calcular_metricas_y_parametros(
        modelo_original, x_train, x_test, y_train, y_test, SALIDA, ENTRADAS
    )
    print(f"Modelo entrenado. Fórmula: {info_modelo['formula']}")
 
    with tempfile.TemporaryDirectory() as carpeta_temporal:
        ruta_modelo_temporal = Path(carpeta_temporal) / "modelo_regresion.json"
 
        print("\n--- 2. GUARDANDO MODELO E INFORMACIÓN EN JSON (EN UNA CARPETA TEMPORAL) ---")
        datos_completos = {
            "version_formato": 1,
            "descripcion": "Modelo de regresión lineal entrenado con datos de vivienda (housing.csv)",
            "columnas_entrada": ENTRADAS,
            "columna_salida": SALIDA,
            **info_modelo
        }
        guardar_modelo_json(ruta_modelo_temporal, datos_completos)
        print(f"Archivo JSON guardado temporalmente en: {ruta_modelo_temporal}")
 
        print("\n--- 3. CARGANDO Y RECONSTRUYENDO DESDE EL ARCHIVO JSON ---")
        datos_cargados = cargar_modelo_json(ruta_modelo_temporal)
        modelo_reconstruido = reconstruir_modelo(datos_cargados)
 
        print("Información asociada recuperada del archivo:")
        print(f"  • Descripción: {datos_cargados['descripcion']}")
        print(f"  • Variables de entrada: {datos_cargados['columnas_entrada']}")
        print(f"  • Columna de salida: {datos_cargados['columna_salida']}")
        print(f"  • Fórmula guardada: {datos_cargados['formula']}")
        print(f"  • R² (Entrenamiento): {datos_cargados['metricas']['entrenamiento']['r2']:.4f}")
        print(f"  • R² (Test): {datos_cargados['metricas']['test']['r2']:.4f}")
        print(f"  • ECM (Entrenamiento): {datos_cargados['metricas']['entrenamiento']['ecm']:.2f}")
        print(f"  • ECM (Test): {datos_cargados['metricas']['test']['ecm']:.2f}")
 
        print("\n--- 4. COMPROBACIÓN DE IGUALDAD EN PREDICCIONES ---")
        nuevo = pd.DataFrame([VALOR_NUEVO])[ENTRADAS]
 
        pred_original = modelo_original.predict(nuevo)[0][0]
        pred_reconstruida = modelo_reconstruido.predict(nuevo)[0][0]
 
        print(f"Valores de entrada de prueba: {VALOR_NUEVO}")
        print(f"Predicción del modelo original     : {pred_original:.2f}")
        print(f"Predicción del modelo reconstruido : {pred_reconstruida:.2f}")
 
        assert np.isclose(pred_original, pred_reconstruida), "¡Las predicciones no coinciden!"
 
        pred_test_original = modelo_original.predict(x_test)
        pred_test_reconstruida = modelo_reconstruido.predict(x_test)
        print(f"Predicciones comparadas sobre el conjunto de test: {len(x_test)}")
 
        assert np.allclose(pred_test_original, pred_test_reconstruida), "¡Las predicciones de test no coinciden!"
        print("\nEl modelo cargado produce las mismas predicciones.")


if __name__ == "__main__":
    main()