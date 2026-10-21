import tkinter as tk
from html import escape
from pathlib import Path
from tkinter import filedialog
from nicegui import run, ui
from diamond_dogs.importador import ImportadorDatos


class Gui:
    """Clase para crear la interfaz gráfica de importación y visualización de datos.

    Attributes
    ----------
    ruta : str
        Ruta del archivo seleccionado por el usuario.
    df : pd.DataFrame
        DataFrame con los datos importados.
    ext : str
        Extensión del archivo importado.
    etiqueta_ruta : Element
        Elemento que muestra la ruta del archivo seleccionado.
    tabla : Element
        Tabla donde se muestran los datos importados.
    mensaje_vacio : Element
        Mensaje que se muestra cuando no hay datos.
    desplegable : Element
        Selector de opciones de la interfaz.
    entrada_texto : Element
        Campo de texto para introducir información.
    etiqueta_mensaje : Element
        Elemento donde se muestra el mensaje generado.

    Methods
    -------
    elegir_ruta()
        Abre el selector de archivos del sistema.
    elegir_archivo()
        Selecciona e importa un archivo.
    mostrar_datos_en_tabla()
        Muestra los datos importados en la tabla.
    mostrar_texto()
        Muestra un mensaje según la opción seleccionada y el texto introducido.
    """

    def __init__(self):
        """Inicializa los atributos y construye los elementos de la interfaz.

        Returns
        -------
        None.
        """
        self.ruta = ""
        self.df = None
        self.ext = ""

        # Contenedor principal de la aplicación.
        with ui.element("div").classes("app"):

            ui.html("Diamond Dogs", tag="h2", sanitize=False).classes("titulo")

            # Contenedor para seleccionar el archivo y mostrar los datos.
            with ui.element("div").classes("importar"):

                with ui.element("div").classes("fila-archivo"):
                    ui.html(
                        "Seleccionar archivo",
                        tag="button",
                        sanitize=False
                    ).classes("boton-archivo").on("click", self.elegir_archivo)

                    self.etiqueta_ruta = ui.html(
                        "Ningún archivo seleccionado",
                        tag="span",
                        sanitize=False
                    ).classes("ruta")

                # Contenedor de la tabla que mostrará los datos importados.
                with ui.element("div").classes("contenedor-tabla"):
                    self.tabla = ui.element("table").classes("tabla")
                    self.mensaje_vacio = ui.html(
                        "Sin datos. Selecciona un archivo para empezar.",
                        tag="p",
                        sanitize=False
                    ).classes("vacio")

            # Contenedor de los controles para introducir y mostrar texto.
            with ui.element("div").classes("formulario"):

                self.desplegable = ui.select(
                    ["Opción 1", "Opción 2", "Opción 3", "Opción 4", "Opción 5"],
                    value="Opción 1",
                ).props('outlined').classes("selector")

                self.entrada_texto = ui.textarea(placeholder="Escribe aquí...")
                self.entrada_texto.props('outlined input-style="height: 250px; resize: none"')
                self.entrada_texto.classes("area-texto")
                self.etiqueta_mensaje = ui.html("", tag="p", sanitize=False).classes("mensaje")

                ui.html(
                    "Mostrar texto",
                    tag="button",
                    sanitize=False
                ).classes("boton-archivo").on("click", self.mostrar_texto)

    def elegir_ruta(self):
        """Abre el selector de archivos del sistema.

        Returns
        -------
        str
            Ruta del archivo seleccionado o una cadena vacía si no se selecciona ninguno.
        """
        raiz = tk.Tk()
        raiz.withdraw()
        raiz.attributes("-topmost", True)
        raiz.update()

        tipos_archivo = (
            ("Archivos compatibles", "*.csv *.xlsx *.xls *.sqlite *.db"),
            ("Archivos CSV", "*.csv"),
            ("Archivos Excel", "*.xlsx *.xls"),
            ("Bases de datos SQLite", "*.sqlite *.db")
        )
        
        ruta = filedialog.askopenfilename(
            title="Seleccionar Dataset",
            filetypes=tipos_archivo
        )
        raiz.update()
        raiz.destroy()
        return ruta

    async def elegir_archivo(self):
        """Selecciona un archivo, lo importa y muestra sus datos.

        Returns
        -------
        None.
        """
        # Ejecuta el selector de archivos sin bloquear el bucle de eventos.
        ruta = await run.io_bound(self.elegir_ruta)

        if not ruta:
            return

        try:
            ruta_absoluta = Path(ruta).resolve()

            self.ruta = str(ruta_absoluta)
            self.etiqueta_ruta.set_content(escape(self.ruta))

            # Importa el archivo mediante la clase ImportadorDatos.
            importador = ImportadorDatos(ruta_absoluta)
            self.df, self.ext = importador.importar()

            # Muestra los datos importados en la tabla de la interfaz.
            self.mostrar_datos_en_tabla()

        except Exception as e:

            ui.notify(str(e), type="negative", position="center", timeout=0, close_button=True)

    def mostrar_datos_en_tabla(self):
        """Muestra las primeras veinte filas del DataFrame en la tabla.

        Returns
        -------
        None.
        """
        if self.df is None:
            return

        self.tabla.clear()
        with self.tabla:
            # Construye la cabecera con los nombres de las columnas.
            with ui.element("thead"):
                with ui.element("tr"):
                    for columna in self.df.columns:
                        ui.html(escape(str(columna)), tag="th", sanitize=False)

            # Construye las filas con los valores del DataFrame.
            with ui.element("tbody"):
                for fila in self.df.astype(str).itertuples(index=False):
                    with ui.element("tr"):
                        for valor in fila:
                            ui.html(escape(valor), tag="td", sanitize=False)

        self.mensaje_vacio.set_visibility(False)

    def mostrar_texto(self):
        """Muestra un mensaje según la opción seleccionada y el texto introducido.

        Returns
        -------
        None.
        """
        texto = self.entrada_texto.value or ""

        # Si no se introduce texto, muestra la opción seleccionada.
        if texto.strip() == "":
            mensaje = f"La opción elegida es: {self.desplegable.value}"
        else:
            mensaje = f"Texto ingresado: {texto}"

        self.etiqueta_mensaje.set_content(escape(mensaje))


def main():
    """Configura la página principal e inicia la aplicación.

    Returns
    -------
    None.
    """
    @ui.page("/")
    def index():
        """Configura la página principal de la interfaz.

        Returns
        -------
        None.
        """
        # Carga los estilos CSS desde el archivo de la aplicación.
        ui.add_css(Path(__file__).with_name("style_interfaz.css").read_text(encoding="utf-8"))
        Gui()

    # Inicia la aplicación NiceGUI.
    ui.run(reload=False, title="Diamond Dogs")


if __name__ == "__main__":
    main()