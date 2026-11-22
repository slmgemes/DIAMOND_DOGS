from diamond_dogs.flujo_de_trabajo import calcular_flujo


def test_mientras_hay_una_operacion_en_curso_no_se_puede_iniciar_ningun_paso():
    """Con ocupado=True, ningún paso está disponible, pero el estado de los pasos no cambia."""
    normal = calcular_flujo(True, True, True, True, False, False)
    ocupado = calcular_flujo(True, True, True, True, False, False, ocupado=True)

    assert any(paso["disponible"] for paso in normal)
    assert not any(paso["disponible"] for paso in ocupado)
    assert [p["estado"] for p in ocupado] == [p["estado"] for p in normal]


def test_con_un_modelo_cargado_tambien_se_bloquea_mientras_hay_una_operacion():
    """Con un modelo cargado y una operación en curso, tampoco se puede predecir."""
    pasos = calcular_flujo(False, False, False, False, True, True, ocupado=True)
    assert not any(paso["disponible"] for paso in pasos)


def test_al_terminar_la_operacion_vuelven_a_estar_disponibles():
    """Con ocupado=False (valor por defecto), los pasos vuelven a estar disponibles."""
    pasos = calcular_flujo(True, False, False, False, False, False)
    assert [p["disponible"] for p in pasos][:2] == [True, True]