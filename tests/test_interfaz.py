import asyncio

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

            await usuario.should_see(content="entrada")
            await usuario.should_not_see(content="Sin datos. Selecciona un archivo")

    asyncio.run(comprobar_renderizado())
