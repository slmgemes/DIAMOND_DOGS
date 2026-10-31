import tkinter as tk
from html import escape
from pathlib import Path
from tkinter import filedialog
from nicegui import run, ui
from diamond_dogs.importador import ImportadorDatos
from diamond_dogs.seleccion import REGRESION_MULTIPLE, validar_seleccion


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
                with ui.element("div").classes(
                    "contenedor-tabla"
                ) as self.contenedor_tabla:
                    self.tabla = ui.element("div").classes("tabla")
                    self.mensaje_vacio = ui.html(
                        "Sin datos. Selecciona un archivo para empezar.",
                        tag="p",
                        sanitize=False
                    ).classes("vacio")

                #contenedor de los selectores para elegir columnas de entrada y salida.
                with ui.element("div").classes(
                    "seleccion-columnas formulario"
                ) as self.contenedor_seleccion:
                    self.sel_features = ui.select(
                        [],
                        label="Columnas de entrada",
                        multiple=REGRESION_MULTIPLE,
                        value=[] if REGRESION_MULTIPLE else None,
                    ).props("outlined").classes("selector")
                    self.sel_target = ui.select(
                        [],
                        label="Columna de salida",
                        value=None,
                    ).props("outlined").classes("selector")
                    self.sel_target.on_value_change(self.al_cambiar_target)
                    ui.button(
                        "Confirmar selección",
                        on_click=self.confirmar_seleccion,
                    ).classes("boton-archivo")
                    self.etiqueta_seleccion = ui.html(
                        "", tag="p", sanitize=False
                    ).classes("mensaje")
                self.contenedor_seleccion.set_visibility(False)

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

    def elegir_archivo(self):
        """Selecciona un archivo, lo importa y muestra sus datos.

        Returns
        -------
        None.
        """
        # Ejecuta el selector de archivos sin bloquear el bucle de eventos.
        ruta = self.elegir_ruta()

        if not ruta:
            return

        try:
            ruta_absoluta = Path(ruta).resolve()

            # Importa el archivo mediante la clase ImportadorDatos.
            importador = ImportadorDatos(ruta_absoluta)
            df_nuevo, ext_nuevo = importador.importar()
            self.df = df_nuevo
            self.ext = ext_nuevo
            self.ruta = str(ruta_absoluta)

            # Muestra los datos importados en la tabla de la interfaz.
            self.etiqueta_ruta.set_content(escape(self.ruta))
            self.actualizar_selectores()
            self.mostrar_datos_en_tabla()

        except Exception as e:
            error_str = str(e)
            
            texto_error = error_str.split(":")[0] if ":" in error_str else error_str
            
            ui.notify(texto_error, type="negative", position="center", timeout=5000)

    def mostrar_datos_en_tabla(self):
        """Muestra todos los datos del DataFrame en una tabla con scroll.

        Returns
        -------
        None.
        """
        #!
        if self.df is None:
            return

        self.tabla.clear()
        #!
        if self.df.empty or len(self.df.columns) == 0:
            self._mostrar_mensaje_vacio(
                "El archivo no contiene datos o columnas para mostrar."
            )
            self.contenedor_seleccion.set_visibility(False)
            return

        # Tabla con scroll virtual: solo dibuja las filas que se ven.
        with self.tabla:
            ui.aggrid.from_pandas(self.df.astype(str).fillna(""),                
                auto_size_columns=False,
                options={"autoSizeStrategy": {"type": "fitCellContents"}},).classes("rejilla")

        self.mensaje_vacio.set_visibility(False)

    #!
    def _mostrar_mensaje_vacio(self, mensaje):
        """Crea o actualiza el mensaje dentro del contenedor de la tabla."""
        if self.mensaje_vacio is None:
            with self.contenedor_tabla:
                self.mensaje_vacio = ui.html(
                    mensaje, tag="p", sanitize=False
                ).classes("vacio")
            return

        self.mensaje_vacio.set_content(mensaje)
        self.mensaje_vacio.set_visibility(True)


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

    def _columnas_features(self):
        """Devuelve las features seleccionadas siempre como lista."""
        valor = self.sel_features.value
        if valor is None:
            return []
        return list(valor) if isinstance(valor, (list, tuple, set)) else [valor]

    def actualizar_selectores(self):
        """Carga las columnas del dataset en los selectores y borra la selección previa.

        Returns
        -------
        None.
        """
        columnas = list(self.df.columns) if self.df is not None else []
        self.features, self.target = [], None
        self.etiqueta_seleccion.set_content("")
        self.sel_features.set_options(
            columnas, value=[] if REGRESION_MULTIPLE else None
        )
        self.sel_target.set_options(columnas, value=None)
        self.contenedor_seleccion.set_visibility(
            bool(columnas) and not self.df.empty
        )

    def al_cambiar_target(self, _=None):
        """Quita de las features la columna elegida como salida.

        Returns
        -------
        None.
        """
        if self.df is None:
            return
        target = self.sel_target.value
        columnas = [c for c in self.df.columns if c != target]
        actuales = [c for c in self._columnas_features() if c != target]
        valor = actuales if REGRESION_MULTIPLE else (actuales[0] if actuales else None)
        self.sel_features.set_options(columnas, value=valor)

    def confirmar_seleccion(self):
        """Valida y registra las columnas elegidas como entrada y salida.

        Returns
        -------
        None.
        """
        features = self._columnas_features()
        target = self.sel_target.value
        errores = validar_seleccion(self.df, features, target, REGRESION_MULTIPLE)

        if errores:
            # Una selección inválida invalida también la confirmada antes.
            self.features, self.target = [], None
            self.etiqueta_seleccion.set_content("")
            ui.notify(
                "\n".join(errores), type="negative", position="center",
                timeout=5000, multi_line=True,
            )
            return

        self.features, self.target = features, target
        self.etiqueta_seleccion.set_content(escape(
            f"Selección confirmada. Entrada: {', '.join(map(str, features))}. "
            f"Salida: {target}."
        ))

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