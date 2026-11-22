from html import escape

PASOS = (
    "Cargar datos",
    "Seleccionar columnas",
    "Separar datos",
    "Preprocesar",
    "Crear modelo",
    "Predecir",
)


def calcular_flujo(hay_datos, seleccion_confirmada, datos_separados,
                   datos_sin_nulos, hay_modelo, modelo_cargado, ocupado=False):
    """Calcula el estado de cada paso del flujo y si se puede realizar.

    Parameters
    ----------
    hay_datos : bool
        Hay un dataset cargado.
    seleccion_confirmada : bool
        Las columnas de entrada y salida están confirmadas.
    datos_separados : bool
        Los datos están separados en entrenamiento y test.
    datos_sin_nulos : bool
        Los datos separados no tienen valores inexistentes.
    hay_modelo : bool
        Hay un modelo creado o cargado.
    modelo_cargado : bool
        El modelo se ha cargado desde un archivo, sin dataset.
    ocupado : bool, optional
        Hay una operación larga en curso: ningún paso se puede iniciar
        hasta que termine. Por defecto False.

    Returns
    -------
    list of dict
        Un diccionario por paso, en orden, con las claves "nombre",
        "estado" ("hecho", "actual", "pendiente" o "no_aplica") y
        "disponible" (True si el paso se puede realizar ahora).
    """
    if modelo_cargado:
        estados = ["hecho"] + ["no_aplica"] * 4 + ["actual"]
        disponibles = [True, False, False, False, False, True]
        return _con_ocupado(
            [
                {"nombre": nombre, "estado": estado, "disponible": disponible}
                for nombre, estado, disponible in zip(PASOS, estados, disponibles)
            ],
            ocupado,
        )

    hechos = [
        hay_datos,
        hay_datos and seleccion_confirmada,
        hay_datos and seleccion_confirmada and datos_separados,
        hay_datos and seleccion_confirmada and datos_separados and datos_sin_nulos,
        hay_modelo,
        False,
    ]
    disponibles = [
        True,
        hay_datos,
        hay_datos and seleccion_confirmada,
        hay_datos and seleccion_confirmada and datos_separados,
        hay_datos and seleccion_confirmada and datos_separados and datos_sin_nulos,
        hay_modelo,
    ]

    pasos = []
    hay_actual = False
    for nombre, hecho, disponible in zip(PASOS, hechos, disponibles):
        if hecho:
            estado = "hecho"
        elif not hay_actual:
            estado = "actual"
            hay_actual = True
        else:
            estado = "pendiente"
        pasos.append({"nombre": nombre, "estado": estado, "disponible": disponible})
    return _con_ocupado(pasos, ocupado)

def _con_ocupado(pasos, ocupado):
    """Si hay una operación en curso, ningún paso se puede iniciar."""
    if ocupado:
        for paso in pasos:
            paso["disponible"] = False
    return pasos

def lineas_estado(nombre_archivo, filas, origen_modelo, nombre_modelo,
                  cambios_sin_guardar):
    """Prepara los textos de la barra de estado.

    Parameters
    ----------
    nombre_archivo : str or None
        Nombre del dataset cargado, o None si no hay ninguno.
    filas : int
        Número de filas del dataset cargado.
    origen_modelo : str or None
        "creado", "cargado" o None si no hay modelo.
    nombre_modelo : str or None
        Nombre del archivo del modelo, si se ha guardado o cargado.
    cambios_sin_guardar : bool
        El modelo actual tiene cambios sin guardar.

    Returns
    -------
    list of tuple
        Pares (texto, aviso). aviso es True si el texto debe destacarse.
    """
    if nombre_archivo:
        filas_texto = f"{filas:,}".replace(",", ".")
        archivo = f"Archivo: {nombre_archivo} ({filas_texto} filas)"
    else:
        archivo = "Archivo: ninguno"
    lineas = [(archivo, False)]

    if origen_modelo is None:
        lineas.append(("Modelo: ninguno", False))
        return lineas

    modelo = f"Modelo: {origen_modelo}"
    if nombre_modelo:
        modelo += f" ({nombre_modelo})"
    lineas.append((modelo, False))

    if cambios_sin_guardar:
        lineas.append(("Cambios sin guardar", True))
    else:
        lineas.append(("Todo guardado", False))
    return lineas


def html_pasos(pasos):
    """Construye el HTML de la barra de pasos.

    Parameters
    ----------
    pasos : list of dict
        Resultado de calcular_flujo.

    Returns
    -------
    str
        HTML de la lista de pasos, con una clase por estado.
    """
    elementos = []
    for numero, paso in enumerate(pasos, start=1):
        estado = paso["estado"]
        if estado == "hecho":
            simbolo = "&#10003;"
        elif estado == "no_aplica":
            simbolo = "&ndash;"
        else:
            simbolo = str(numero)
        clase = estado.replace("_", "-")
        elementos.append(
            f'<li class="paso {clase}">'
            f'<span class="paso-circulo">{simbolo}</span>'
            f'<span class="paso-nombre">{escape(paso["nombre"])}</span>'
            "</li>"
        )
    return '<ol class="pasos-lista">' + "".join(elementos) + "</ol>"


def html_estado(lineas):
    """Construye el HTML de la barra de estado.

    Parameters
    ----------
    lineas : list of tuple
        Resultado de lineas_estado.

    Returns
    -------
    str
        HTML con un elemento por texto, destacando los avisos.
    """
    return "".join(
        f'<span class="estado{" aviso" if aviso else ""}">{escape(texto)}</span>'
        for texto, aviso in lineas
    )
