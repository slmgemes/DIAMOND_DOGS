import tkinter as tk
from html import escape
from pathlib import Path
from tkinter import filedialog
from nicegui import run, ui
from diamond_dogs.importador import ImportadorDatos





class Gui:
    def __init__(self):
        self.ruta = ""
        self.df = None
        self.ext = ""

        with ui.element("div").classes("app"):
            

            ui.html("Diamond Dogs", tag="h2", sanitize=False).classes("titulo")
            with ui.element("div").classes("importar"):

                with ui.element("div").classes("fila-archivo"):
                    ui.html("Seleccionar archivo", tag="button", sanitize=False).classes("boton-archivo").on("click", self.elegir_archivo)
                    self.etiqueta_ruta = ui.html("Ningún archivo seleccionado", tag="span", sanitize=False).classes("ruta")

                with ui.element("div").classes("contenedor-tabla"):
                    self.tabla =ui.element("table").classes("tabla")
                    self.mensaje_vacio = ui.html(
                        "Sin datos. Selecciona un archivo para empezar.", tag="p", sanitize=False
                    ).classes("vacio")
            with ui.element("div").classes("formulario"):

                self.desplegable = ui.select(
                    ["Opción 1", "Opción 2", "Opción 3", "Opción 4", "Opción 5"],
                    value="Opción 1",
                ).props('outlined').classes("selector")

                self.entrada_texto = ui.textarea(placeholder="Escribe aquí...")
                self.entrada_texto.props('outlined input-style="height: 250px; resize: none"')
                self.entrada_texto.classes("area-texto")
                self.etiqueta_mensaje = ui.html("", tag="p", sanitize=False).classes("mensaje")

                ui.html("Mostrar texto", tag="button", sanitize=False).classes("boton-archivo").on("click", self.mostrar_texto)


    def mostrar_texto(self):
        texto = self.entrada_texto.value or ""

        if texto.strip() == "":
            mensaje = f"La opción elegida es: {self.desplegable.value}"
        else:
            mensaje = f"Texto ingresado: {texto}"

        self.etiqueta_mensaje.set_content(escape(mensaje))
            

    def elegir_ruta(self):
        raiz = tk.Tk()
        raiz.withdraw()
        raiz.attributes("-topmost", True)
        ruta = filedialog.askopenfilename(title="Elige un archivo")
        raiz.destroy()
        return ruta

    async def elegir_archivo(self):
        ruta = await run.io_bound(self.elegir_ruta)
        if ruta:
            self.ruta = ruta
            self.etiqueta_ruta.set_content(escape(ruta))

            importador = ImportadorDatos(self.ruta)
            self.df, self.ext = importador.importar()
            self.mostrar_datos_en_tabla()

    def mostrar_datos_en_tabla(self):
        if self.df is None:
            return

        head = self.df.head(20)

        self.tabla.clear()
        with self.tabla:
            with ui.element("thead"):
                with ui.element("tr"):
                    for columna in head.columns:
                        ui.html(escape(str(columna)), tag="th", sanitize=False)

            with ui.element("tbody"):
                for fila in head.astype(str).itertuples(index=False):
                    with ui.element("tr"):
                        for valor in fila:
                            ui.html(escape(valor), tag="td", sanitize=False)

        self.mensaje_vacio.set_visibility(False)


def main():
    @ui.page("/")
    def index():
        ui.add_css(Path(__file__).with_name("style.css").read_text(encoding="utf-8"))
        Gui()

    ui.run(reload=False, title="Diamond Dogs")