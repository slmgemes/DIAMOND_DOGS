import pandas as pd

def identificar_nulos(x_train, x_test, y_train, y_test):

    nulos_x_train = x_train.isnull().sum()
    nulos_x_test = x_test.isnull().sum()
    nulos_y_train = y_train.isnull().sum()
    nulos_y_test = y_test.isnull().sum()


    total_nulos = (nulos_x_train.sum()
        + nulos_x_test.sum()
        + nulos_y_train.sum()
        + nulos_y_test.sum()
    )
    if total_nulos == 0:
        return {"nulos":False,
                "mensaje": "No se han detectado valores inexistentes en el conjunto de entrenamiento ni de test. Puede continuar sin preprocesar.",
                "nulos_x_train":nulos_x_train,
                "nulos_x_test":nulos_x_test,
                "nulos_y_train":nulos_y_train,
                "nulos_y_test":nulos_y_test
                }
    return {"nulos":True,
            "mensaje": "Todavía quedan valores inexistentes.",
            "nulos_x_train":nulos_x_train,
            "nulos_x_test":nulos_x_test,
            "nulos_y_train":nulos_y_train,
            "nulos_y_test":nulos_y_test
            }

def eliminar_nulos(x_train, x_test, y_train, y_test):

    x_train_copy, x_test_copy = x_train.copy(), x_test.copy()
    y_train_copy, y_test_copy = y_train.copy(), y_test.copy()

    if isinstance(y_train_copy, pd.Series):
        target_columnas = [y_train_copy.name] if y_train_copy.name is not None else ["target"]
        y_train_df = y_train_copy.to_frame()
        y_test_df = y_test_copy.to_frame()
    else:
        target_columnas = list(y_train_copy.columns)
        y_train_df = y_train_copy
        y_test_df = y_test_copy
    
    filas_train = len(x_train_copy)
    filas_test = len(x_test_copy)

    train_completo = pd.concat([x_train_copy, y_train_df], axis=1)
    test_completo = pd.concat([x_test_copy, y_test_df], axis=1)

    train_limpio = train_completo.dropna()
    test_limpio = test_completo.dropna() 

    if len(train_limpio) == 0 or len(test_limpio) == 0:
        raise ValueError("La eliminación de filas dejaría vacío el conjunto de entrenamiento o el de test.")

    filas_eliminadas_train = filas_train - len(train_limpio)
    filas_eliminadas_test = filas_test - len(test_limpio)

    x_train_copy = train_limpio.drop(columns=target_columnas)
    y_train_res = train_limpio[target_columnas]
    x_test_copy = test_limpio.drop(columns=target_columnas)
    y_test_res = test_limpio[target_columnas]
    
    if isinstance(y_train, pd.Series):
        y_train_copy = y_train_res.iloc[:, 0]
        y_test_copy = y_test_res.iloc[:, 0]
    else:
        y_train_copy = y_train_res
        y_test_copy = y_test_res   

    resumen = {
    "estrategia": "eliminar",
    "filas_eliminadas_train": filas_eliminadas_train,
    "filas_eliminadas_test": filas_eliminadas_test,
    }
    return x_train_copy, x_test_copy, y_train_copy, y_test_copy, resumen

def rellenar_media(x_train, x_test, y_train, y_test):

    x_train_copy, x_test_copy = x_train.copy(), x_test.copy()
    y_train_copy, y_test_copy = y_train.copy(), y_test.copy()
    nulos_antes_train = x_train_copy.isnull().sum().sum() + y_train_copy.isnull().sum().sum()
    nulos_antes_test = x_test_copy.isnull().sum().sum() + y_test_copy.isnull().sum().sum()

    media_x = x_train_copy.mean()
    media_y = y_train_copy.mean()

    x_train_copy = x_train_copy.fillna(media_x)
    y_train_copy = y_train_copy.fillna(media_y)
    x_test_copy = x_test_copy.fillna(media_x)
    y_test_copy = y_test_copy.fillna(media_y)

    resumen = {
        "estrategia": "media",
        "valores_rellenados_train": nulos_antes_train,
        "valores_rellenados_test": nulos_antes_test,
    }
    
    return x_train_copy, x_test_copy, y_train_copy, y_test_copy, resumen

def rellenar_mediana(x_train, x_test, y_train, y_test):

    x_train_copy, x_test_copy = x_train.copy(), x_test.copy()
    y_train_copy, y_test_copy = y_train.copy(), y_test.copy()
    nulos_antes_train = x_train_copy.isnull().sum().sum() + y_train_copy.isnull().sum().sum()
    nulos_antes_test = x_test_copy.isnull().sum().sum() + y_test_copy.isnull().sum().sum()

    mediana_x = x_train_copy.median()
    mediana_y = y_train_copy.median()

    x_train_copy = x_train_copy.fillna(mediana_x)
    y_train_copy = y_train_copy.fillna(mediana_y)
    x_test_copy = x_test_copy.fillna(mediana_x)
    y_test_copy = y_test_copy.fillna(mediana_y)

    resumen = {
        "estrategia": "mediana",
        "valores_rellenados_train": nulos_antes_train,
        "valores_rellenados_test": nulos_antes_test,
    }
    
    return x_train_copy, x_test_copy, y_train_copy, y_test_copy, resumen

def rellenar_constante(x_train, x_test, y_train, y_test, cte):

    if cte is None or (isinstance(cte, str) and cte.strip() == ""):
        raise ValueError("Se requiere un valor constante para esta estrategia.")

    try:
        cte_f = float(cte)
    except (ValueError, TypeError):
        raise ValueError("El valor constante no puede ser texto. Debes introducir un número válido.")

    x_train_copy, x_test_copy = x_train.copy(), x_test.copy()
    y_train_copy, y_test_copy = y_train.copy(), y_test.copy()
    nulos_antes_train = x_train_copy.isnull().sum().sum() + y_train_copy.isnull().sum().sum()
    nulos_antes_test = x_test_copy.isnull().sum().sum() + y_test_copy.isnull().sum().sum()

    relleno_x = pd.Series(cte_f, index=x_train_copy.columns)
    if isinstance(y_train_copy, pd.Series):
        y_train_copy = y_train_copy.fillna(cte_f)
        y_test_copy = y_test_copy.fillna(cte_f)
    else:
        relleno_y = pd.Series(cte_f, index=y_train_copy.columns) if not y_train_copy.empty else pd.Series(dtype=float)
        y_train_copy = y_train_copy.fillna(relleno_y)
        y_test_copy = y_test_copy.fillna(relleno_y)

    x_train_copy = x_train_copy.fillna(relleno_x)
    x_test_copy = x_test_copy.fillna(relleno_x)

    resumen = {
        "estrategia": "constante",
        "valores_rellenados_train": nulos_antes_train,
        "valores_rellenados_test": nulos_antes_test,
    }
    
    return x_train_copy, x_test_copy, y_train_copy, y_test_copy, resumen