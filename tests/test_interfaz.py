import asyncio
from types import SimpleNamespace
from unittest.mock import patch

from nicegui import ui
import pandas as pd
from nicegui.testing import user_simulation

from diamond_dogs.interfaz import Gui


def modelo_persistido(descripcion=""):
    return {
        "version_formato": 1,
        "descripcion": descripcion,
        "columnas_entrada": ["x"],
        "columna_salida": "y",
        "coeficientes": [2.0],
        "termino_independiente": 5.0,
        "formula": "y = 2.0000 * x + 5.0000",
        "metricas": {
            "entrenamiento": {"filas": 3, "ecm": 0.0, "r2": 1.0},
            "test": {"filas": 2, "ecm": 1.0, "r2": -3.0},
        },
    }


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


def test_modelo_cargado_muestra_resultados():
    async def comprobar_modelo_cargado():
        interfaces = []

        def crear_interfaz():
            interfaces.append(Gui())

        async with user_simulation(crear_interfaz) as usuario:
            await usuario.open("/")
            interfaz = interfaces[0]
            with usuario:
                with (
                    patch.object(
                        interfaz, "elegir_ruta_modelo", return_value="modelo.model.json"
                    ),
                    patch(
                        "diamond_dogs.interfaz.leer_modelo",
                        return_value=modelo_persistido("Descripción guardada"),
                    ),
                ):
                    interfaz.cargar_modelo_archivo()

            await usuario.should_see(content="y = 2.0000 * x + 5.0000")
            await usuario.should_see(content="Modelo cargado correctamente.")
            await usuario.should_see(content="Entradas: x")
            await usuario.should_see(content="Descripción guardada")
            await usuario.should_see(content="ECM")
            await usuario.should_not_see(kind=ui.aggrid)
            await usuario.should_not_see(kind=ui.pyplot)

    asyncio.run(comprobar_modelo_cargado())


def test_archivo_invalido_conserva_el_modelo_y_permite_reintentar():
    async def comprobar_reintento():
        interfaces = []

        def crear_interfaz():
            interfaces.append(Gui())

        async with user_simulation(crear_interfaz) as usuario:
            await usuario.open("/")
            interfaz = interfaces[0]
            with usuario:
                interfaz.mostrar_modelo_cargado(
                    modelo_persistido("Modelo anterior"), "anterior.model.json"
                )
                modelo_anterior = interfaz.datos_modelo
                with (
                    patch.object(
                        interfaz,
                        "elegir_ruta_modelo",
                        side_effect=["dañado.model.json", "nuevo.model.json"],
                    ),
                    patch(
                        "diamond_dogs.interfaz.leer_modelo",
                        side_effect=[
                            ValueError("El archivo no contiene un modelo válido."),
                            modelo_persistido("Modelo nuevo"),
                        ],
                    ),
                ):
                    interfaz.cargar_modelo_archivo()
                    assert interfaz.datos_modelo is modelo_anterior
                    interfaz.cargar_modelo_archivo()

            assert interfaz.datos_modelo["descripcion"] == "Modelo nuevo"

    asyncio.run(comprobar_reintento())


def test_guardar_modelo_cargado_actualiza_ruta_y_limpia_cambios(tmp_path):
    async def comprobar_guardado():
        interfaces = []
        destino = tmp_path / "modelo actualizado.model.json"

        def crear_interfaz():
            interfaces.append(Gui())

        async with user_simulation(crear_interfaz) as usuario:
            await usuario.open("/")
            interfaz = interfaces[0]
            with usuario:
                interfaz.mostrar_modelo_cargado(
                    modelo_persistido("Descripción original"), "original.model.json"
                )
                interfaz.actualizar_descripcion_modelo(
                    SimpleNamespace(value="Descripción actualizada")
                )
                with patch.object(
                    interfaz, "elegir_ruta_guardado", return_value=str(destino)
                ):
                    interfaz.guardar_modelo_archivo()

            assert not interfaz.hay_cambios_sin_guardar()
            assert interfaz.ruta_modelo == destino.resolve()
            from diamond_dogs.persistencia_modelos import cargar_modelo
            assert cargar_modelo(destino)["descripcion"] == "Descripción actualizada"

    asyncio.run(comprobar_guardado())


def test_dialogo_guardado_propone_archivo_cargado_y_confirma_sobrescritura(tmp_path):
    async def comprobar_dialogo():
        interfaces = []
        carpeta = tmp_path / "carpeta con ñ"
        carpeta.mkdir()
        origen = carpeta / "modelo año.model.json"
        origen.write_text("modelo previo", encoding="utf-8")
        raiz = SimpleNamespace(
            withdraw=lambda: None,
            attributes=lambda *_: None,
            update=lambda: None,
            destroy=lambda: None,
        )

        def crear_interfaz():
            interfaces.append(Gui())

        async with user_simulation(crear_interfaz) as usuario:
            await usuario.open("/")
            interfaz = interfaces[0]
            with usuario:
                interfaz.mostrar_modelo_cargado(
                    modelo_persistido("Descripción"), str(origen)
                )
                with (
                    patch("diamond_dogs.interfaz.tk.Tk", return_value=raiz),
                    patch(
                        "diamond_dogs.interfaz.filedialog.asksaveasfilename",
                        return_value=str(origen),
                    ) as dialogo,
                    patch(
                        "diamond_dogs.interfaz.messagebox.askyesno",
                        return_value=False,
                    ) as confirmar,
                ):
                    assert interfaz.elegir_ruta_guardado() == ""

            assert dialogo.call_args.kwargs["initialdir"] == str(carpeta)
            assert dialogo.call_args.kwargs["initialfile"] == origen.name
            confirmar.assert_called_once()

    asyncio.run(comprobar_dialogo())


def test_descripcion_modificada_marca_modelo_cargado_como_pendiente():
    async def comprobar_estado():
        interfaces = []

        def crear_interfaz():
            interfaces.append(Gui())

        async with user_simulation(crear_interfaz) as usuario:
            await usuario.open("/")
            interfaz = interfaces[0]
            with usuario:
                interfaz.mostrar_modelo_cargado(modelo_persistido(), "modelo.model.json")
            assert not interfaz.hay_cambios_sin_guardar()
            assert interfaz.entrada_descripcion_modelo.value == ""

            with usuario:
                interfaz.actualizar_descripcion_modelo(
                    SimpleNamespace(value="Descripción nueva")
                )
            assert interfaz.hay_cambios_sin_guardar()

    asyncio.run(comprobar_estado())


def test_cancelar_carga_modelo_conserva_el_modelo_actual():
    async def comprobar_cancelacion():
        interfaces = []

        def crear_interfaz():
            interfaces.append(Gui())

        async with user_simulation(crear_interfaz) as usuario:
            await usuario.open("/")
            interfaz = interfaces[0]
            with usuario:
                interfaz.mostrar_modelo_cargado(
                    modelo_persistido("Descripción original"), "original.model.json"
                )
                interfaz.actualizar_descripcion_modelo(
                    SimpleNamespace(value="Cambios pendientes")
                )
                with (
                    patch.object(
                        interfaz, "elegir_ruta_modelo", return_value="nuevo.model.json"
                    ),
                    patch(
                        "diamond_dogs.interfaz.leer_modelo",
                        return_value=modelo_persistido("Nuevo"),
                    ),
                    patch.object(
                        interfaz, "_confirmar_reemplazo_con_cambios", return_value=False
                    ),
                ):
                    interfaz.cargar_modelo_archivo()

            assert interfaz.datos_modelo["descripcion"] == "Cambios pendientes"
            assert interfaz.hay_cambios_sin_guardar()

    asyncio.run(comprobar_cancelacion())


def test_cancelar_carga_dataset_conserva_modelo_con_cambios(tmp_path):
    async def comprobar_cancelacion():
        interfaces = []
        archivo = tmp_path / "datos.csv"
        archivo.write_text("x,y\n1,2\n", encoding="utf-8")

        def crear_interfaz():
            interfaces.append(Gui())

        async with user_simulation(crear_interfaz) as usuario:
            await usuario.open("/")
            interfaz = interfaces[0]
            with usuario:
                interfaz.mostrar_modelo_cargado(
                    modelo_persistido("Descripción original"), "original.model.json"
                )
                interfaz.actualizar_descripcion_modelo(
                    SimpleNamespace(value="Cambios pendientes")
                )
                with (
                    patch.object(interfaz, "elegir_ruta", return_value=str(archivo)),
                    patch.object(
                        interfaz, "_confirmar_reemplazo_con_cambios", return_value=False
                    ),
                ):
                    await interfaz.elegir_archivo()

            assert interfaz.df is None
            assert interfaz.datos_modelo["descripcion"] == "Cambios pendientes"
            assert interfaz.hay_cambios_sin_guardar()

    asyncio.run(comprobar_cancelacion())
