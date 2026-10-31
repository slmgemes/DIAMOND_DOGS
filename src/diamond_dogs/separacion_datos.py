from sklearn.model_selection import train_test_split

def separar_datos(df,entrada_s, salida , porcentaje_test, semilla=42):
    """Divide los datos en entrenamiento y test de forma aleatoria y reproducible.

    Parameters
    ----------
    df : pd.DataFrame
        Datos importados.
    entrada_s : list of str
        Columnas de entrada.
    salida : str
        Columna de salida.
    porcentaje_test : int or float
        Porcentaje de filas para test (entre 1 y 99).
    semilla : int, optional
        Semilla para que la división sea reproducible. Por defecto 42.

    Returns
    -------
    tuple
        x_train, x_test, y_train, y_test.

    Raises
    ------
    ValueError
        Si el porcentaje, la semilla o el número de filas no son válidos.
    """


    # Porcentaje: número entre 1 y 99.
    if not isinstance(porcentaje_test, (int, float)) or not 1 <= porcentaje_test <= 99 :
        raise ValueError("El porcentaje de test debe ser un número entre 1 y 99.")

    # Semilla: número entero → la parte decimal tiene que ser 0.
    if not isinstance(semilla, (int, float)) or semilla % 1 != 0 or semilla < 0:
        raise ValueError("La semilla debe ser un número entero mayor o igual que 0.")

    # Mínimo de filas.
    filas = len(df)
    if filas < 5:
        raise ValueError(
            f"El dataset tiene {filas} filas y se necesitan al menos 5 para separarlo."
        )
    
    x = df[entrada_s]
    y = df[[salida]]

    #ningun conjunto puede quedar vacío, por eso se hace un try-except
    try:
        x_train, x_test, y_train, y_test = train_test_split(
            x, y,
            test_size=porcentaje_test / 100,
            random_state=int(semilla),
        )
    except ValueError:
        raise ValueError(
            f"Con {filas} filas y un {porcentaje_test}% de test, algún conjunto "
            "quedaría vacío. Elige otro porcentaje."
    )

    return x_train, x_test, y_train, y_test

