from diamond_dogs.flujo_de_trabajo import calcular_flujo, html_estado, html_pasos, lineas_estado


def estados(pasos):
    return [paso["estado"] for paso in pasos]


def disponibles(pasos):
    return [paso["disponible"] for paso in pasos]


def flujo(**kwargs):
    """Calcula el flujo partiendo de una aplicación recién abierta."""
    estado = dict(hay_datos=False, seleccion_confirmada=False, datos_separados=False,
                  datos_sin_nulos=False, hay_modelo=False, modelo_cargado=False)
    estado.update(kwargs)
    return calcular_flujo(**estado)


def test_al_iniciar_solo_se_puede_cargar_datos():
    """Al iniciar, el paso 1 es el actual y es el único disponible."""
    pasos = flujo()
    assert estados(pasos) == ["actual"] + ["pendiente"] * 5
    assert disponibles(pasos) == [True, False, False, False, False, False]


def test_con_datos_toca_seleccionar_columnas():
    """Con un dataset cargado, el paso 1 está hecho y toca el 2."""
    pasos = flujo(hay_datos=True)
    assert estados(pasos) == ["hecho", "actual"] + ["pendiente"] * 4
    assert disponibles(pasos) == [True, True, False, False, False, False]


def test_con_seleccion_confirmada_toca_separar():
    """Con las columnas confirmadas, toca separar los datos."""
    pasos = flujo(hay_datos=True, seleccion_confirmada=True)
    assert estados(pasos) == ["hecho", "hecho", "actual"] + ["pendiente"] * 3
    assert disponibles(pasos) == [True, True, True, False, False, False]


def test_con_nulos_toca_preprocesar_y_no_se_puede_crear_el_modelo():
    """Con valores inexistentes, toca preprocesar y crear el modelo no está disponible."""
    pasos = flujo(hay_datos=True, seleccion_confirmada=True, datos_separados=True)
    assert estados(pasos) == ["hecho"] * 3 + ["actual", "pendiente", "pendiente"]
    assert disponibles(pasos) == [True, True, True, True, False, False]


def test_sin_nulos_el_preprocesado_esta_hecho_y_toca_crear_el_modelo():
    """Sin valores inexistentes, el paso 4 se da por hecho y toca crear el modelo."""
    pasos = flujo(hay_datos=True, seleccion_confirmada=True, datos_separados=True,
                  datos_sin_nulos=True)
    assert estados(pasos) == ["hecho"] * 4 + ["actual", "pendiente"]
    assert disponibles(pasos) == [True, True, True, True, True, False]


def test_con_modelo_creado_se_puede_predecir():
    """Con un modelo creado, todos los pasos anteriores están hechos y toca predecir."""
    pasos = flujo(hay_datos=True, seleccion_confirmada=True, datos_separados=True,
                  datos_sin_nulos=True, hay_modelo=True)
    assert estados(pasos) == ["hecho"] * 5 + ["actual"]
    assert disponibles(pasos) == [True] * 6


def test_con_modelo_cargado_solo_se_puede_predecir():
    """Con un modelo cargado no hay dataset: los pasos 2 a 5 no aplican."""
    pasos = flujo(hay_modelo=True, modelo_cargado=True)
    assert estados(pasos) == ["hecho"] + ["no_aplica"] * 4 + ["actual"]
    assert disponibles(pasos) == [True, False, False, False, False, True]


def test_un_paso_no_esta_hecho_si_falta_uno_anterior():
    """Una separación sin dataset no cuenta: no se salta ningún paso."""
    pasos = flujo(datos_separados=True, datos_sin_nulos=True)
    assert estados(pasos) == ["actual"] + ["pendiente"] * 5


def test_estado_sin_archivo_ni_modelo():
    """Sin archivo ni modelo, la barra lo indica."""
    assert lineas_estado(None, 0, None, None, False) == [
        ("Archivo: ninguno", False), ("Modelo: ninguno", False),
    ]


def test_estado_con_archivo_muestra_las_filas_con_separador_de_miles():
    """El número de filas se escribe con punto como separador de miles."""
    lineas = lineas_estado("housing.csv", 20640, None, None, False)
    assert lineas[0] == ("Archivo: housing.csv (20.640 filas)", False)


def test_estado_con_modelo_creado_y_cambios_sin_guardar():
    """Un modelo recién creado avisa de que tiene cambios sin guardar."""
    lineas = lineas_estado("datos.csv", 10, "creado", None, True)
    assert lineas[1] == ("Modelo: creado", False)
    assert lineas[2] == ("Cambios sin guardar", True)


def test_estado_con_modelo_cargado_y_guardado():
    """Un modelo cargado sin cambios indica que todo está guardado."""
    lineas = lineas_estado(None, 0, "cargado", "vivienda.model.json", False)
    assert lineas == [
        ("Archivo: ninguno", False),
        ("Modelo: cargado (vivienda.model.json)", False),
        ("Todo guardado", False),
    ]


def test_html_pasos_marca_cada_estado():
    """El HTML de los pasos tiene una clase por estado y un símbolo por paso."""
    html = html_pasos(flujo(hay_datos=True))
    assert html.count('class="paso ') == 6
    assert 'class="paso hecho"' in html
    assert 'class="paso actual"' in html
    assert "&#10003;" in html            # el paso hecho lleva una marca
    assert ">2</span>" in html           # el paso actual lleva su número


def test_html_pasos_con_modelo_cargado_usa_no_aplica():
    """Los pasos que no aplican llevan su propia clase."""
    html = html_pasos(flujo(hay_modelo=True, modelo_cargado=True))
    assert html.count('class="paso no-aplica"') == 4


def test_html_estado_destaca_los_avisos():
    """Solo el texto de aviso lleva la clase aviso, y el texto se escapa."""
    html = html_estado([("Archivo: <a&b>.csv", False), ("Cambios sin guardar", True)])
    assert html.count('class="estado aviso"') == 1
    assert "&lt;a&amp;b&gt;" in html
