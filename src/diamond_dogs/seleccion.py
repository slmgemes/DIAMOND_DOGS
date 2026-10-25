import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

# True: regresión múltiple (varias, hace regresión múltiple). False: regresión simple (una).
REGRESION_MULTIPLE = True


def _es_numerica(serie: pd.Series) -> bool:
    """Indica si una columna es numérica (los booleanos no cuentan)."""
    return is_numeric_dtype(serie) and not is_bool_dtype(serie)


def validar_seleccion(df, features, target, multiple=REGRESION_MULTIPLE):
    """Valida la selección de columnas de entrada y salida.

    Parámetros
    ----------
    df : pd.DataFrame
        Dataset cargado.
    features : list
        Columnas de entrada seleccionadas.
    target : object
        Columna de salida seleccionada (None si no hay ninguna).
    multiple : bool
        True si se admite más de una columna de entrada.

    Devuelve
    -------
    list[str]
        Mensajes de error. Lista vacía si la selección es válida.
    """
    errores = []
    features = list(features or [])

    if not features:
        errores.append("Falta seleccionar al menos una columna de entrada (features).")
    elif not multiple and len(features) > 1:
        errores.append("En regresión simple solo se puede elegir una columna de entrada.")

    if target is None or target == "":
        errores.append("Falta seleccionar la columna de salida (target).")
        target = None

    seleccionadas = list(dict.fromkeys(features + ([target] if target is not None else [])))

    inexistentes = [c for c in seleccionadas if c not in df.columns]
    if inexistentes:
        errores.append(
            "Columnas que no existen en el dataset: "
            + ", ".join(map(str, inexistentes)) + "."
        )

    if target is not None and target in features:
        errores.append(f"La columna '{target}' no puede ser a la vez entrada y salida.")

    no_numericas = [
        c for c in seleccionadas if c in df.columns and not _es_numerica(df[c])
    ]
    if no_numericas:
        errores.append(
            "Columnas no numéricas que no se pueden usar en una regresión lineal: "
            + ", ".join(map(str, no_numericas)) + "."
        )

    return errores