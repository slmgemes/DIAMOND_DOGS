"""Lógica del modelo de regresión lineal: entrenar, métricas y fórmula."""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


def entrenar_modelo(x_train, y_train):
    """Entrena un modelo de regresión lineal solo con el conjunto de entrenamiento.

    Parameters
    ----------
    x_train : pd.DataFrame
        Columnas de entrada del conjunto de entrenamiento.
    y_train : pd.DataFrame
        Columna de salida del conjunto de entrenamiento.

    Returns
    -------
    LinearRegression
        Modelo entrenado.
    """
    modelo = LinearRegression()
    modelo.fit(x_train, y_train)
    return modelo


def calcular_metricas(modelo:LinearRegression, x_train, x_test, y_train, y_test):
    """Calcula el R² y el ECM en entrenamiento y en test.

    Parameters
    ----------
    modelo : LinearRegression
        Modelo entrenado.
    x_train, x_test : pd.DataFrame
        Columnas de entrada de entrenamiento y de test.
    y_train, y_test : pd.DataFrame
        Columna de salida de entrenamiento y de test.

    Returns
    -------
    dict
        Claves "r2_train", "r2_test", "ecm_train" y "ecm_test".
    """

    
    prediccion_train = modelo.predict(x_train)
    prediccion_test = modelo.predict(x_test)

    return {
        "r2_train": r2_score(y_train, prediccion_train),
        "r2_test": r2_score(y_test, prediccion_test),
        "ecm_train": mean_squared_error(y_train, prediccion_train),
        "ecm_test": mean_squared_error(y_test, prediccion_test),
    }


def escribir_formula(salida, entradas, modelo:LinearRegression):
    """Escribe la fórmula del modelo con los nombres de las columnas.

    Los números se muestran siempre con 2 decimales, y los negativos restando.

    Parameters
    ----------
    salida : str
        Nombre de la columna de salida.
    entradas : list of str
        Nombres de las columnas de entrada.
    modelo : LinearRegression
        Modelo entrenado, con la salida como DataFrame.
        
    Returns
    -------
    str
        Fórmula, por ejemplo "precio = 4.20 * edad - 15.30".
    """


    # Como y es un DataFrame, coef_ es [[c1, c2, ...]] e intercept_ es [t].
    coeficientes = modelo.coef_[0]
    termino = modelo.intercept_[0]

    formula = f"{salida} ="

    # Un trozo por cada columna de entrada.
    for i in range(len(entradas)):
        coef = coeficientes[i]
        if i == 0:
            formula += f" {coef:.2f} * {entradas[i]}"
        elif coef < 0:
            formula += f" - {abs(coef):.2f} * {entradas[i]}"
        else:
            formula += f" + {coef:.2f} * {entradas[i]}"

    # Al final, el término independiente con su signo.
    if termino < 0:
        formula += f" - {abs(termino):.2f}"
    else:
        formula += f" + {termino:.2f}"

    return formula

