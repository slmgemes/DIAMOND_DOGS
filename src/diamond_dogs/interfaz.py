import tkinter as tk
from html import escape
from pathlib import Path
from tkinter import filedialog
from nicegui import  ui
from diamond_dogs.importador import ImportadorDatos
from diamond_dogs.seleccion import REGRESION_MULTIPLE, validar_seleccion, es_regresion_multiple, obtener_columnas_disponibles
from diamond_dogs.separacion_datos import separar_datos
from diamond_dogs.preprocesado import identificar_nulos, eliminar_nulos, rellenar_media, rellenar_mediana, rellenar_constante


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

        Return  s
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
                    ).classes("boton").on("click", self.elegir_archivo)

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
                    ).props("outlined use-chips").classes("selector")
                    self.sel_target = ui.select(
                        [],
                        label="Columna de salida",
                        value=None,
                    ).props("outlined").classes("selector")
                    self.sel_target.on_value_change(self.al_cambiar_target)
                    ui.html(
                        "Confirmar selección",
                        tag="button",
                        sanitize=False
                    ).classes("boton").on("click", self.confirmar_seleccion)
                    self.etiqueta_seleccion = ui.html(
                        "", tag="p", sanitize=False
                    ).classes("mensaje-seleccion")
                self.contenedor_seleccion.set_visibility(False)

                #contenedor de separacion de datos

                with ui.element("div").classes(
                    "porcentajes"
                ) as self.contenedor_porcentajes:
                    # Porcentaje de test: lo escribe el usuario.
                    self.entrada_test = ui.number(
                        label="Test (%)", value=20
                    ).props("outlined").classes("entrada-test")

                    # Porcentaje de entrenamiento: se calcula solo y no se puede tocar.
                    self.entrada_train = ui.number(
                        label="Entrenamiento (%)", value=80
                    ).props("outlined").classes("entrada-train")
                    self.entrada_train.disable()

                    # Semilla para que la separación sea reproducible.
                    self.entrada_semilla = ui.number(
                        label="Semilla", value=42
                    ).props("outlined").classes("entrada-semilla")

                    ui.html(
                        "Separar datos",
                        tag="button",
                        sanitize=False
                    ).classes("boton").on("click", self.separacion_datos)


                    self.contenedor_porcentajes.set_visibility(False)

                    # Cuando cambia el test, el entrenamiento se actualiza solo.
                    self.entrada_train.bind_value_from(
                        self.entrada_test, "value", backward=lambda v: 100 - v if v is not None else None,
                    )

                # Resultado de la separación: oculto hasta pulsar "Separar datos".
                with ui.element("div").classes(
                    "resultado-separacion"
                ) as self.resultado_separacion:
                    self.etiqueta_confirmacion = ui.html(
                        "", tag="p", sanitize=False
                    ).classes("mensaje-confirmacion")
                    self.etiqueta_filas = ui.html(
                        "", tag="p", sanitize=False
                    ).classes("mensaje-filas")

                    self.resultado_separacion.set_visibility(False)

                # Contenedor de preprocesado.

                with ui.element("div").classes(
                    "contenedor-preprocesado"
                ) as self.contenedor_preprocesado:
                    ui.html("Tratamiento de valores inexistentes", tag="h3", sanitize=False)

                    self.etiqueta_diagnostico = ui.html("", tag="div", sanitize=False)

                    with ui.element("div").classes("bloque-opciones-nulos") as self.bloque_opciones_nulos:
                        self.radio_estrategia = ui.radio(
                            options={
                                "eliminar": "Eliminar las filas que contengan valores inexistentes",
                                "media": "Rellenar con la media de cada columna",
                                "mediana": "Rellenar con la mediana de cada columna",
                                "constante": "Rellenar con un valor constante"
                            },
                            value="eliminar"
                        ).classes("radio-estrategia")

                        self.entrada_constante = ui.number(
                            label="Valor constante", value=0
                        ).props("outlined").classes("entrada-constante")
                        self.entrada_constante.bind_visibility_from(
                            self.radio_estrategia, "value", lambda v: v == "constante"
                        )

                        ui.html(
                            "Aplicar preprocesado",
                            tag="button",
                            sanitize=False
                        ).classes("boton").on("click", self.aplicar_preprocesado)

                    self.etiqueta_resultado_preprocesado = ui.html("", tag="p", sanitize=False)

                    self.contenedor_preprocesado.set_visibility(False)

                    #contenedor del modelo de regresion lineal

                with ui.element("div").classes("contenedor-modelo") as self.contenedor_modelo:
                    ui.html("Crear modelo",tag="button",sanitize=False
                            ).classes("boton").on("click", self.crear_modelo)
                    self.contenedor_modelo.set_visibility(False)




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
                options={"defaultColDef": {"flex": 1, "minWidth": 200}},).classes("rejilla")

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
        self.etiqueta_seleccion.set_visibility(False)
        self.sel_features.set_options(
            columnas, value=[] if REGRESION_MULTIPLE else None
        )
        self.sel_target.set_options(columnas, value=None)
        self.contenedor_seleccion.set_visibility(
            bool(columnas) and not self.df.empty
        )
        self.x_train = self.x_test = self.y_train = self.y_test = None
        self.contenedor_porcentajes.set_visibility(False)
        self.resultado_separacion.set_visibility(False)
        self.contenedor_preprocesado.set_visibility(False)
        self.contenedor_modelo.set_visibility(False)

    def al_cambiar_target(self, _=None):
        """Quita de las features la columna elegida como salida.

        Returns
        -------
        None.
        """
        if self.df is None:
            return
        target = self.sel_target.value

        columnas = obtener_columnas_disponibles(self.df, target)
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
            self.es_multiple = False
            self.contenedor_porcentajes.set_visibility(False)
            self.etiqueta_seleccion.set_visibility(False)
            self.resultado_separacion.set_visibility(False)
            self.contenedor_modelo.set_visibility(False)
            ui.notify(
                "\n".join(errores), type="negative", position="center",
                timeout=5000, multi_line=True,
            )
            return

        self.features, self.target = features, target
        self.es_multiple = es_regresion_multiple(self.features)
        self.etiqueta_seleccion.set_visibility(True)
        self.etiqueta_seleccion.set_content(
            "<b style='font-size: 22px; '>Selección confirmada</b><br>"
            f"Entrada: {escape(', '.join(map(str, features)))}<br>"
            f"Salida: {escape(str(target))}"
        )

        self.x_train = self.x_test = self.y_train = self.y_test = None
        self.contenedor_porcentajes.set_visibility(True)
        self.resultado_separacion.set_visibility(False)
        self.contenedor_preprocesado.set_visibility(False)
        self.contenedor_modelo.set_visibility(False)

    def separacion_datos(self):
        """Separa los datos en entrenamiento y test y muestra el resultado.

        Returns
        -------
        None.
        """
        try:
            self.x_train, self.x_test, self.y_train, self.y_test = separar_datos(
                self.df, self.features, self.target,
                self.entrada_test.value, semilla=self.entrada_semilla.value
            )

            self.x_train_base = None

        except ValueError as e:
            # Muestra el mensaje de separar_datos y no realiza la separación.
            self.x_train = self.x_test = self.y_train = self.y_test = None
            self.resultado_separacion.set_visibility(False)
            ui.notify(str(e), type="negative", position="center", timeout=5000)
            self.contenedor_modelo.set_visibility(False)
            return

        self.etiqueta_confirmacion.set_content("División realizada correctamente.")
        self.etiqueta_filas.set_content(
            f"Entrenamiento: {len(self.x_train)} filas<br>"
            f"Test: {len(self.x_test)} filas"
        )
        self.resultado_separacion.set_visibility(True)
        self.iniciar_preprocesado()

    def iniciar_preprocesado(self):
        resultado_nulos = identificar_nulos(self.x_train, self.x_test, self.y_train, self.y_test)
        self.contenedor_preprocesado.set_visibility(True)

        if not resultado_nulos["nulos"]:
            self.etiqueta_diagnostico.set_content(
                f"<b style='color: green;'>{escape(resultado_nulos['mensaje'])}</b>"
            )
            self.bloque_opciones_nulos.set_visibility(False)
            self.etiqueta_resultado_preprocesado.set_content("")
            self.contenedor_modelo.set_visibility(True)
        else:
            x_train = resultado_nulos["nulos_x_train"]
            x_test = resultado_nulos["nulos_x_test"]
            y_train = resultado_nulos["nulos_y_train"]
            y_test = resultado_nulos["nulos_y_test"]

            desglose = "<b>Se han detectado valores inexistentes (NaN):</b><br><ul>"
            for col, val in x_train.items():
                if val > 0:
                    desglose += f"<li>Entrada '{col}' (Train): {val} nulos</li>"
            for col, val in x_test.items():
                if val > 0:
                    desglose += f"<li>Entrada '{col}' (Test): {val} nulos</li>"
            for col, val in y_train.items():
                if val > 0:
                    desglose += f"<li>Salida '{col}' (Train): {val} nulos</li>"
            for col, val in y_test.items():
                if val > 0:
                    desglose += f"<li>Salida '{col}' (Test): {val} nulos</li>"
            desglose += "</ul>"

            self.etiqueta_diagnostico.set_content(desglose)
            self.bloque_opciones_nulos.set_visibility(True)
            self.etiqueta_resultado_preprocesado.set_content("")
            self.contenedor_modelo.set_visibility(False)

    def aplicar_preprocesado(self):
        estrategia = self.radio_estrategia.value
        cte = self.entrada_constante.value

        try:
            if not hasattr(self, 'x_train_base') or self.x_train_base is None:
                self.x_train_base = self.x_train.copy()
                self.x_test_base = self.x_test.copy()
                self.y_train_base = self.y_train.copy()
                self.y_test_base = self.y_test.copy()

            xt_input = self.x_train_base.copy()
            xte_input = self.x_test_base.copy()
            yt_input = self.y_train_base.copy()
            yte_input = self.y_test_base.copy()
            
            if estrategia == "eliminar":
                self.x_train, self.x_test, self.y_train, self.y_test, resumen = eliminar_nulos(
                    xt_input, xte_input, yt_input, yte_input
                )
                msg = (
                    f"Filas eliminadas — Entrenamiento: {resumen['filas_eliminadas_train']}, "
                    f"Test: {resumen['filas_eliminadas_test']}"
                )
            elif estrategia == "media":
                self.x_train, self.x_test, self.y_train, self.y_test, resumen = rellenar_media(
                    xt_input, xte_input, yt_input, yte_input
                )
                msg = (
                    f"Valores rellenados con la media — Total entrenamiento: {resumen['valores_rellenados_train']}, "
                    f"Total test: {resumen['valores_rellenados_test']}"
                )
            elif estrategia == "mediana":
                self.x_train, self.x_test, self.y_train, self.y_test, resumen = rellenar_mediana(
                    xt_input, xte_input, yt_input, yte_input
                )
                msg = (
                    f"Valores rellenados con la mediana — Total entrenamiento: {resumen['valores_rellenados_train']}, "
                    f"Total test: {resumen['valores_rellenados_test']}"
                )
            elif estrategia == "constante":
                self.x_train, self.x_test, self.y_train, self.y_test, resumen = rellenar_constante(
                    xt_input, xte_input, yt_input, yte_input, cte
                )
                msg = (
                    f"Valores rellenados con constante ({cte}) — Total entrenamiento: {resumen['valores_rellenados_train']}, "
                    f"Total test: {resumen['valores_rellenados_test']}"
                )
            else:
                return

            self.etiqueta_resultado_preprocesado.set_content(f"<b>{msg}</b>")
            resultado_nulos = identificar_nulos(self.x_train, self.x_test, self.y_train, self.y_test)
            if not resultado_nulos["nulos"]:
                self.etiqueta_diagnostico.set_content(
                    "<b>¡Ya no quedan valores inexistentes (NaN) en los datasets!</b>"
                )
                self.contenedor_modelo.set_visibility(True)
            else:
                self.etiqueta_diagnostico.set_content(f"<b>{escape(resultado_nulos['mensaje'])}</b>")
                self.contenedor_modelo.set_visibility(False)

            self.bloque_opciones_nulos.set_visibility(True)

        except ValueError as e:
            ui.notify(str(e), type="negative", position="center", timeout=5000)

    def crear_modelo(self):
        """Crea el modelo de regresión lineal (pendiente de implementar).

        Returns
        -------
        None.
        """
        ui.notify("Botón pulsado: aquí se creará el modelo", position="center")

    

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
    ui.run(reload=False, title="Diamond Dogs", reconnect_timeout=120.0)


if __name__ == "__main__":
    main()