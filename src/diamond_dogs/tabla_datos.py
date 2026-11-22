from pandas.api.types import is_bool_dtype, is_numeric_dtype


def preparar_tabla(df):
    """Convierte un DataFrame en las columnas y las filas de la tabla.

    Los valores numéricos se mantienen como números, para que la tabla los
    ordene correctamente; el resto de valores se pasan a texto. Los valores
    inexistentes se dejan en blanco. Los campos de la tabla se llaman c0, c1...
    para que funcionen los nombres de columna con puntos o repetidos.

    Parameters
    ----------
    df : pd.DataFrame
        Datos importados.

    Returns
    -------
    dict
        "columnDefs": definición de cada columna (campo, título y tipo).
        "rowData": una fila por cada fila del DataFrame, sin omitir ninguna.
    """
    campos = []
    definiciones = []
    columnas_valores = []

    for i, nombre in enumerate(df.columns):
        serie = df.iloc[:, i]
        campo = f"c{i}"
        definicion = {"field": campo, "headerName": str(nombre)}

        if is_numeric_dtype(serie) and not is_bool_dtype(serie):
            definicion["type"] = "numericColumn"
            valores = serie.astype(object).where(serie.notna(), None).tolist()
        else:
            valores = serie.astype(str).mask(serie.isna(), "").tolist()

        campos.append(campo)
        definiciones.append(definicion)
        columnas_valores.append(valores)

    filas = [dict(zip(campos, fila)) for fila in zip(*columnas_valores)]
    return {"columnDefs": definiciones, "rowData": filas}
