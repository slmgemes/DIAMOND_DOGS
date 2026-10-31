from sklearn.model_selection import train_test_split

def separar_datos(df,entrada_s, salida , porcentaje_test, semilla=42):
    """Divide los datos en entrenamiento y test de forma aleatoria y reproducible.

    Parameters
    ----------
    df : pd.DataFrame
        Datos importados.
    features : list of str
        Columnas de entrada.
    target : str
        Columna de salida.
    porcentaje_test : int
        Porcentaje de filas para test (1-99).
    semilla : int, optional
        Semilla para que la división sea reproducible. Por defecto 42.

    Returns
    -------
    tuple
        X_train, X_test, y_train, y_test.
    """
    x = df[entrada_s]
    y = df[[salida]]

    return train_test_split(
        x, y,
        test_size=porcentaje_test / 100,
        random_state=int(semilla),
    )