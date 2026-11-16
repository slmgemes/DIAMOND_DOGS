import asyncio
from types import SimpleNamespace

from nicegui import ui
import pandas as pd
from nicegui.testing import user_simulation

from diamond_dogs.interfaz import Gui


def test_aviso_vacio_se_elimina_al_cargar_tabla():
    async def comprobar_renderizado():
        interfaces = []

        def crear_interfaz():
            interfaces.append(Gui())

        async with user_simulation(crear_interfaz) as usuario:
            await usuario.open("/")
            await usuario.should_see(content="Sin datos. Selecciona un archivo")

            interfaz = interfaces[0]
            with usuario:
                interfaz.df = pd.DataFrame({"entrada": [1], "salida": [2]})
                interfaz.mostrar_datos_en_tabla()

            await usuario.should_see(kind=ui.aggrid) 
            await usuario.should_not_see(content="Sin datos. Selecciona un archivo")

    asyncio.run(comprobar_renderizado())


def test_descripcion_disponible_tras_crear_modelo_y_se_limpia_al_ocultarlo():
    async def comprobar_descripcion():
        interfaces = []

        def crear_interfaz():
            interfaces.append(Gui())

        async with user_simulation(crear_interfaz) as usuario:
            await usuario.open("/")
            interfaz = interfaces[0]
            await usuario.should_not_see(kind=ui.textarea)

            with usuario:
                interfaz.contenedor_modelo.set_visibility(True)
                interfaz.features = ["entrada"]
                interfaz.target = "salida"
                interfaz.x_train = pd.DataFrame({"entrada": [1, 2, 3]})
                interfaz.x_test = pd.DataFrame({"entrada": [4, 5]})
                interfaz.y_train = pd.DataFrame({"salida": [2, 4, 6]})
                interfaz.y_test = pd.DataFrame({"salida": [8, 10]})
                interfaz.crear_modelo()

            await usuario.should_see(kind=ui.textarea)
            with usuario:
                interfaz.actualizar_descripcion_modelo(
                    SimpleNamespace(value="Predice el resultado para el caso de uso.")
                )
            assert interfaz.datos_modelo["descripcion"] == (
                "Predice el resultado para el caso de uso."
            )

            with usuario:
                interfaz.crear_modelo()
            assert interfaz.datos_modelo["descripcion"] == ""
            assert interfaz.entrada_descripcion_modelo.value == ""

            with usuario:
                interfaz.ocultar_modelo()
            await usuario.should_not_see(kind=ui.textarea)
            assert interfaz.datos_modelo is None

    asyncio.run(comprobar_descripcion())
