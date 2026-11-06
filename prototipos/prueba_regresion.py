"""Prueba de concepto: modelo de regresión lineal con scikit-learn, sin interfaz.

Ejecutar desde la carpeta del proyecto:
    uv run python prototipos/prueba_regresion.py
"""

from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from diamond_dogs.importador import ImportadorDatos
from diamond_dogs.separacion_datos import separar_datos
from diamond_dogs.preprocesado import eliminar_nulos

# ---------- Configuración: cámbiala según el dataset ----------
ARCHIVO = Path(__file__).parent.parent / "data" / "housing.csv"
ENTRADAS = ["median_income", "housing_median_age", "total_rooms"]
SALIDA = "median_house_value"
PORCENTAJE_TEST = 20
SEMILLA = 42
VALOR_NUEVO = {"median_income": 5.0, "housing_median_age": 20, "total_rooms": 2000}


def escribir_formula(salida, entradas, coeficientes, termino):
    """Escribe la fórmula del modelo con los nombres de las columnas.

    Parameters
    ----------
    salida : str
        Nombre de la columna de salida.
    entradas : list of str
        Nombres de las columnas de entrada.
    coeficientes : list of float
        Un coeficiente por cada columna de entrada.
    termino : float
        Término independiente.

    Returns
    -------
    str
        Fórmula, por ejemplo "precio = 4.2 * edad + 15.3".
    """
    formula = f"{salida} ="

    # Un trozo por cada columna de entrada.
    for i in range(len(entradas)):
        coef = round(coeficientes[i], 2)
        if i == 0:
            formula += f" {coef} * {entradas[i]}"
        elif coef < 0:
            formula += f" - {abs(coef)} * {entradas[i]}"
        else:
            formula += f" + {coef} * {entradas[i]}"

    # Al final, el término independiente con su signo.
    termino = round(termino, 2)
    if termino < 0:
        formula += f" - {abs(termino)}"
    else:
        formula += f" + {termino}"

    return formula


def main():
    """Ejecuta los pasos de la prueba de concepto y muestra los resultados.

    Returns
    -------
    None.
    """
    # 1. Cargar los datos con el importador de la aplicación.
    df, _ = ImportadorDatos(ARCHIVO).importar()
    print(f"1. Datos cargados: {len(df)} filas")

    # 2. Separar en entrenamiento y test.
    x_train, x_test, y_train, y_test = separar_datos(
        df, ENTRADAS, SALIDA, PORCENTAJE_TEST, semilla=SEMILLA
    )
    # LinearRegression no acepta NaN: se eliminan las filas afectadas.
    x_train, x_test, y_train, y_test, resumen = eliminar_nulos(
        x_train, x_test, y_train, y_test
    )
    print(
        f"2. Separados: {len(x_train)} filas de entrenamiento y {len(x_test)} de test "
        f"(eliminadas por NaN: {resumen['filas_eliminadas_train']} y "
        f"{resumen['filas_eliminadas_test']})"
    )

    # 3. Entrenar el modelo con el conjunto de entrenamiento.
    modelo = LinearRegression()
    modelo.fit(x_train, y_train)
    print("3. Modelo entrenado")

    # 4. Coeficientes, término independiente y fórmula.
    # coef_ es [[c1, c2, ...]] es un dataframe y intercept_ es [t].
    coeficientes = modelo.coef_[0]
    termino = modelo.intercept_[0]
    print("4. " + escribir_formula(SALIDA, ENTRADAS, coeficientes, termino))

    # 5. Métricas en entrenamiento y en test.
    prediccion_train = modelo.predict(x_train)
    prediccion_test = modelo.predict(x_test)
    print(
        f"5. ECM → entrenamiento: {round(mean_squared_error(y_train, prediccion_train), 2)}"
        f"   test: {round(mean_squared_error(y_test, prediccion_test), 2)}"
    )
    print(
        f"   R²  → entrenamiento: {round(r2_score(y_train, prediccion_train), 4)}"
        f"   test: {round(r2_score(y_test, prediccion_test), 4)}"
    )

    # 6. Predicción para un valor de entrada nuevo.
    nuevo = pd.DataFrame([VALOR_NUEVO])[ENTRADAS]
    prediccion = modelo.predict(nuevo)[0][0]
    print(f"6. Predicción para {VALOR_NUEVO}: {SALIDA} = {round(prediccion, 2)}")


if __name__ == "__main__":
    main()