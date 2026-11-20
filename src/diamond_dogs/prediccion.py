def prediccion(modelo, datos_usuario):
    """Calcula la salida del modelo con los valores que escribió el usuario.

    Parameters
    ----------
    modelo : DatosModelo
        Datos del modelo, creado o cargado.
    datos_usuario : list of str
        Textos escritos en los campos, en el mismo orden que las columnas de entrada.

    Returns
    -------
    float
        Valor predicho de la salida.

    Raises
    ------
    ValueError
        Si falta algún valor o alguno no es un número.
    """
    columnas = modelo["columnas_entrada"]

    faltan = []
    no_validos = []
    numeros = []
    for i in range(len(columnas)):
        texto = datos_usuario[i].strip().replace(",", ".")
        if texto == "":
            faltan.append(columnas[i])
        else:
            try:
                numeros.append(float(texto))
            except ValueError:
                no_validos.append(columnas[i])

    if faltan:
        raise ValueError("Faltan valores para: " + ", ".join(faltan))
    if no_validos:
        raise ValueError("Valor no numérico en: " + ", ".join(no_validos))

    resultado = modelo["termino_independiente"]
    for i in range(len(columnas)):
        resultado += modelo["coeficientes"][i] * numeros[i]
    return resultado