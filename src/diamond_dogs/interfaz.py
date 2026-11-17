import tkinter as tk
from html import escape
from pathlib import Path
from tkinter import filedialog, messagebox
from nicegui import  ui
from diamond_dogs.importador import ImportadorDatos
from diamond_dogs.seleccion import REGRESION_MULTIPLE, validar_seleccion, es_regresion_multiple, obtener_columnas_disponibles
from diamond_dogs.separacion_datos import separar_datos
from diamond_dogs.preprocesado import identificar_nulos, eliminar_nulos, rellenar_media, rellenar_mediana, rellenar_constante
from diamond_dogs.crear_modelo import (
    DatosModelo,
    actualizar_descripcion,
    calcular_metricas,
    crear_datos_modelo,
    datos_grafico,
    entrenar_modelo,
    escribir_formula,
)
from diamond_dogs.persistencia_modelos import (
    EXTENSION,
    agregar_extension,
    cargar_modelo as leer_modelo,
    existe_archivo,
    guardar_modelo,
)
import matplotlib.pyplot as plt

class Gui:
    """Interfaz gráfica de la aplicación.

    Permite importar un archivo de datos, verlo en una tabla, elegir las
    columnas de entrada y de salida, separar los datos en entrenamiento y
    test, tratar los valores inexistentes y crear un modelo de regresión
    lineal con su fórmula, sus métricas y su gráfico.

    Attributes
    ----------
    ruta : str
        Ruta del archivo seleccionado por el usuario.
    df : pd.DataFrame
        DataFrame con los datos importados.
    ext : str
        Extensión del archivo importado.
    features : list of str
        Columnas de entrada confirmadas.
    target : str
        Columna de salida confirmada.
    es_multiple : bool
        Indica si la regresión tiene varias columnas de entrada.
    x_train : pd.DataFrame
        Columnas de entrada del conjunto de entrenamiento.
    x_test : pd.DataFrame
        Columnas de entrada del conjunto de test.
    y_train : pd.DataFrame
        Columna de salida del conjunto de entrenamiento.
    y_test : pd.DataFrame
        Columna de salida del conjunto de test.
    x_train_base : pd.DataFrame
        Copia de x_train antes de tratar los valores inexistentes.
    x_test_base : pd.DataFrame
        Copia de x_test antes de tratar los valores inexistentes.
    y_train_base : pd.DataFrame
        Copia de y_train antes de tratar los valores inexistentes.
    y_test_base : pd.DataFrame
        Copia de y_test antes de tratar los valores inexistentes.
    modelo : LinearRegression
        Modelo creado, o None si todavía no hay ninguno.
    datos_modelo : DatosModelo
        Información del modelo y sus datos asociados, incluida la descripción.
    metricas : dict
        Métricas del modelo creado, o None si todavía no hay ninguno.
    formula : str
        Fórmula del modelo creado, o una cadena vacía si todavía no hay ninguno.
    etiqueta_ruta : Element
        Texto con la ruta del archivo seleccionado.
    contenedor_tabla : Element
        Contenedor de la tabla de datos.
    tabla : Element
        Tabla donde se muestran los datos importados.
    mensaje_vacio : Element
        Mensaje que se muestra cuando no hay datos.
    contenedor_seleccion : Element
        Contenedor de los selectores de columnas.
    sel_features : Element
        Selector de las columnas de entrada.
    sel_target : Element
        Selector de la columna de salida.
    etiqueta_seleccion : Element
        Mensaje con la selección confirmada.
    contenedor_porcentajes : Element
        Contenedor de la separación de datos.
    entrada_test : Element
        Campo del porcentaje de test.
    entrada_train : Element
        Campo del porcentaje de entrenamiento, calculado automáticamente.
    entrada_semilla : Element
        Campo de la semilla de la separación.
    resultado_separacion : Element
        Contenedor del resultado de la separación.
    etiqueta_confirmacion : Element
        Mensaje de separación realizada correctamente.
    etiqueta_filas : Element
        Número de filas de entrenamiento y de test.
    contenedor_preprocesado : Element
        Contenedor del tratamiento de valores inexistentes.
    etiqueta_diagnostico : Element
        Valores inexistentes detectados en cada columna.
    bloque_opciones_nulos : Element
        Contenedor de las opciones de preprocesado.
    radio_estrategia : Element
        Selector de la estrategia de preprocesado.
    entrada_constante : Element
        Campo del valor constante para rellenar.
    etiqueta_resultado_preprocesado : Element
        Resultado del preprocesado aplicado.
    contenedor_modelo : Element
        Contenedor del botón "Crear modelo" y de sus resultados.
    resultado_modelo : Element
        Contenedor de los resultados del modelo.
    etiqueta_modelo : Element
        Mensaje de modelo creado correctamente.
    etiqueta_formula : Element
        Fórmula del modelo.
    tabla_metricas : Element
        Tabla con el R² y el ECM de entrenamiento y de test.
    contenedor_grafico : Element
        Contenedor del gráfico del ajuste.
    entrada_descripcion_modelo : Element
        Área de texto para la descripción opcional del modelo.

    Methods
    -------
    elegir_ruta()
        Abre el selector de archivos del sistema.
    elegir_archivo()
        Selecciona e importa un archivo.
    mostrar_datos_en_tabla()
        Muestra los datos importados en la tabla.
    actualizar_selectores()
        Carga las columnas del archivo en los selectores.
    al_cambiar_target()
        Quita de las entradas la columna elegida como salida.
    confirmar_seleccion()
        Valida y registra las columnas elegidas.
    separacion_datos()
        Separa los datos en entrenamiento y test.
    iniciar_preprocesado()
        Busca valores inexistentes en los datos separados.
    aplicar_preprocesado()
        Aplica la estrategia elegida a los valores inexistentes.
    crear_modelo()
        Crea el modelo y muestra su fórmula, sus métricas y su gráfico.
    ocultar_modelo()
        Oculta el botón "Crear modelo" y borra el modelo anterior.
    mostrar_boton_modelo()
        Muestra el botón "Crear modelo".
    actualizar_descripcion_modelo(evento)
        Actualiza la descripción del modelo a partir del área de texto.
    cargar_modelo_archivo()
        Carga un modelo .model.json y muestra sus resultados.
    elegir_ruta_guardado()
        Abre el diálogo de guardado y pide confirmación si el archivo ya existe.
    guardar_modelo_archivo()
        Pide dónde guardar el modelo y lo guarda en un archivo.
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
        self.modelo = None
        self.datos_modelo: DatosModelo | None = None
        self.metricas = None
        self.formula = ""
        self._modelo_guardado = False
        self._descripcion_guardada = ""
        self.ruta_modelo: Path | None = None

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
                    ui.html(
                        "Cargar modelo",
                        tag="button",
                        sanitize=False
                    ).classes("boton").on("click", self.cargar_modelo_archivo)

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

                    

                # Contenedor del modelo: oculto hasta que se pueda crear.
                with ui.element("div").classes("contenedor-modelo") as self.contenedor_modelo:
                    self.boton_crear_modelo = ui.html(
                        "Crear modelo",
                        tag="button",
                        sanitize=False
                    ).classes("boton").on("click", self.crear_modelo)

                    # Resultados del modelo: ocultos hasta crearlo.
                    with ui.element("div").classes("resultado-modelo") as self.resultado_modelo:
                        self.etiqueta_modelo = ui.html("Modelo creado correctamente.", tag="p", sanitize=False).classes("mensaje-confirmacion")
                        self.etiqueta_formula = ui.html("", tag="p", sanitize=False).classes("formula-modelo")
                        self.etiqueta_columnas_modelo = ui.html("", tag="p", sanitize=False)
                        self.tabla_metricas = ui.html("", tag="div", sanitize=False).classes("tabla-metricas")
                        self.contenedor_grafico = ui.element("div").classes("grafico-modelo")
                        self.entrada_descripcion_modelo = ui.textarea(
                            label="Descripción (opcional)",
                            placeholder="¿En qué consiste este modelo y para qué se creó?",
                        ).props("outlined").classes("descripcion-modelo")
                        self.entrada_descripcion_modelo.on_value_change(
                            self.actualizar_descripcion_modelo
                        )
                        ui.html(
                            "Guardar modelo",
                            tag="button",
                            sanitize=False
                        ).classes("boton").on("click", self.guardar_modelo_archivo)
                    self.resultado_modelo.set_visibility(False)
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

            if not self._confirmar_reemplazo_con_cambios(
                "Se descartarán los cambios sin guardar del modelo actual. "
                "¿Quieres cargar el nuevo dataset?"
            ):
                return

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

        self.contenedor_tabla.set_visibility(True)
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
        """Muestra un mensaje dentro del contenedor de la tabla.

        Parameters
        ----------
        mensaje : str
            Texto que se muestra.

        Returns
        -------
        None.
        """
        
        if self.mensaje_vacio is None:
            with self.contenedor_tabla:
                self.mensaje_vacio = ui.html(
                    mensaje, tag="p", sanitize=False
                ).classes("vacio")
            return

        self.mensaje_vacio.set_content(mensaje)
        self.mensaje_vacio.set_visibility(True)

    def _columnas_features(self):
        """Devuelve las columnas de entrada seleccionadas siempre como lista.

        Returns
        -------
        list
            Columnas de entrada seleccionadas, o una lista vacía si no hay ninguna.
        """

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
        self.ocultar_modelo()

    def hay_cambios_sin_guardar(self):
        """Indica si el modelo actual es nuevo o cambió desde su último guardado."""
        return self.datos_modelo is not None and (
            not self._modelo_guardado
            or self.datos_modelo["descripcion"] != self._descripcion_guardada
        )

    def _confirmar_reemplazo_con_cambios(self, mensaje):
        if not self.hay_cambios_sin_guardar():
            return True

        raiz = tk.Tk()
        raiz.withdraw()
        raiz.attributes("-topmost", True)
        try:
            return messagebox.askyesno(
                "Cambios sin guardar",
                mensaje,
                parent=raiz,
            )
        finally:
            raiz.destroy()

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
            self.x_train = self.x_test = self.y_train = self.y_test = None
            self.contenedor_porcentajes.set_visibility(False)
            self.etiqueta_seleccion.set_visibility(False)
            self.resultado_separacion.set_visibility(False)
            self.contenedor_preprocesado.set_visibility(False)   
            self.ocultar_modelo()
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
        self.ocultar_modelo()

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
            self.x_train_base = None       
            self.resultado_separacion.set_visibility(False)
            self.contenedor_preprocesado.set_visibility(False)  
            ui.notify(str(e), type="negative", position="center", timeout=5000)
            self.ocultar_modelo()
            return

        self.etiqueta_confirmacion.set_content("División realizada correctamente.")
        self.etiqueta_filas.set_content(
            f"Entrenamiento: {len(self.x_train)} filas<br>"
            f"Test: {len(self.x_test)} filas"
        )
        self.resultado_separacion.set_visibility(True)
        self.iniciar_preprocesado()

    def iniciar_preprocesado(self):
        """Busca valores inexistentes en los datos separados y muestra el resultado.

        Returns
        -------
        None.
        """

        resultado_nulos = identificar_nulos(self.x_train, self.x_test, self.y_train, self.y_test)
        self.contenedor_preprocesado.set_visibility(True)

        if not resultado_nulos["nulos"]:
            self.etiqueta_diagnostico.set_content(
                f"<b style='color: green;'>{escape(resultado_nulos['mensaje'])}</b>"
            )
            self.bloque_opciones_nulos.set_visibility(False)
            self.etiqueta_resultado_preprocesado.set_content("")
            self.mostrar_boton_modelo()
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
            self.ocultar_modelo()

    def aplicar_preprocesado(self):
        """Aplica a los valores inexistentes la estrategia elegida por el usuario.

        Returns
        -------
        None.
        """
                
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
                self.mostrar_boton_modelo()
            else:
                self.etiqueta_diagnostico.set_content(f"<b>{escape(resultado_nulos['mensaje'])}</b>")
                self.ocultar_modelo()

            self.bloque_opciones_nulos.set_visibility(True)

        except (ValueError,TypeError) as e:
            ui.notify(str(e), type="negative", position="center", timeout=5000)

    def crear_modelo(self):
        """Crea el modelo y muestra su fórmula, sus métricas y su gráfico.

        Returns
        -------
        None.
        """
        self.modelo = None
        self.datos_modelo = None
        self.entrada_descripcion_modelo.value = ""
        self.entrada_descripcion_modelo.update()

        try:
            self.modelo = entrenar_modelo(self.x_train, self.y_train)
            metricas = calcular_metricas(
                self.modelo, self.x_train, self.x_test, self.y_train, self.y_test
            )
            formula = escribir_formula(self.target, self.features, self.modelo)
            self.datos_modelo = crear_datos_modelo(
                self.modelo, self.features, self.target, formula, metricas,
                self.x_train, self.x_test,
            )
            self._modelo_guardado = False
            self._descripcion_guardada = ""
            self.ruta_modelo = None
            datos= datos_grafico(
                self.modelo, self.x_train, self.x_test, self.y_train, self.y_test
            )
        except Exception as e:
            # Cualquier error: se avisa y la aplicación sigue funcionando.
            self.modelo = None
            self.datos_modelo = None
            self.entrada_descripcion_modelo.value = ""
            self.entrada_descripcion_modelo.update()
            self.metricas = None
            self.formula = ""
            self.resultado_modelo.set_visibility(False)
            ui.notify(f"No se pudo crear el modelo: {e}", type="negative",
                    position="center", timeout=5000)
            return

        self.metricas = metricas
        self.formula = formula
        self.etiqueta_modelo.set_content("Modelo creado correctamente.")
        self.boton_crear_modelo.set_visibility(True)
        self._mostrar_informacion_modelo()

        self.contenedor_grafico.clear()
        self.contenedor_grafico.set_visibility(True)
        with self.contenedor_grafico:
            with ui.pyplot(figsize=(8, 5)).classes("grafico"):
                plt.scatter(datos["x_train"], datos["y_train"], s=4, color="#b8893b",
                            label="Entrenamiento", rasterized=True)
                plt.scatter(datos["x_test"], datos["y_test"], s=6, color="#7a2e2e",
                            marker="^", label="Test", rasterized=True)
                plt.plot(datos["linea_x"], datos["linea_y"], color="#3b2f2f",
                         linewidth=2, label=datos["nombre_linea"])
                plt.xlabel(datos["eje_x"])
                plt.ylabel(datos["eje_y"])
                plt.legend()

        self.resultado_modelo.set_visibility(True)

    def _mostrar_informacion_modelo(self):
        datos = self.datos_modelo
        if datos is None:
            return

        self.etiqueta_formula.set_content(escape(datos["formula"]))
        self.etiqueta_columnas_modelo.set_content(
            f"Entradas: {escape(', '.join(datos['columnas_entrada']))}<br>"
            f"Salida: {escape(datos['columna_salida'])}"
        )
        metricas = datos["metricas"]
        self.tabla_metricas.set_content(
            "<table>"
            "<tr><th>Métrica</th><th>Entrenamiento</th><th>Test</th></tr>"
            f"<tr><td>R<sup>2</sup></td>"
            f"<td>{metricas['entrenamiento']['r2']:.4f}</td>"
            f"<td>{metricas['test']['r2']:.4f}</td></tr>"
            f"<tr><td>ECM</td>"
            f"<td>{metricas['entrenamiento']['ecm']:,.2f}</td>"
            f"<td>{metricas['test']['ecm']:,.2f}</td></tr>"
            "</table>"
        )
        self.entrada_descripcion_modelo.value = datos["descripcion"]
        self.entrada_descripcion_modelo.update()

    def cargar_modelo_archivo(self):
        """Pide un modelo guardado, lo valida y lo muestra en la interfaz."""
        ruta = self.elegir_ruta_modelo()
        if not ruta:
            return

        try:
            datos = leer_modelo(ruta)
        except ValueError as e:
            ui.notify(str(e), type="negative", position="center", timeout=5000)
            return

        if not self._confirmar_reemplazo_con_cambios(
            "Se descartarán los cambios sin guardar del modelo actual. "
            "¿Quieres cargar el modelo seleccionado?"
        ):
            return

        self.mostrar_modelo_cargado(datos, ruta)

    def elegir_ruta_modelo(self):
        """Abre el selector de modelos .model.json y devuelve su ruta."""
        raiz = tk.Tk()
        raiz.withdraw()
        raiz.attributes("-topmost", True)
        try:
            return filedialog.askopenfilename(
                title="Cargar modelo",
                filetypes=(("Modelos de Diamond Dogs", "*" + EXTENSION),),
                parent=raiz,
            )
        finally:
            raiz.destroy()

    def mostrar_modelo_cargado(self, datos: DatosModelo, ruta: str = ""):
        """Muestra un modelo guardado sin sus secciones asociadas al dataset."""
        self.df = None
        self.ext = ""
        self.ruta = ""
        self.features = list(datos["columnas_entrada"])
        self.target = datos["columna_salida"]
        self.es_multiple = len(self.features) > 1
        self.x_train = self.x_test = self.y_train = self.y_test = None
        self.modelo = None
        self.datos_modelo = datos
        self.metricas = {
            "r2_train": datos["metricas"]["entrenamiento"]["r2"],
            "r2_test": datos["metricas"]["test"]["r2"],
            "ecm_train": datos["metricas"]["entrenamiento"]["ecm"],
            "ecm_test": datos["metricas"]["test"]["ecm"],
        }
        self.formula = datos["formula"]
        self._modelo_guardado = True
        self._descripcion_guardada = datos["descripcion"]
        self.ruta_modelo = Path(ruta).resolve() if ruta else None

        self.contenedor_tabla.set_visibility(False)
        self.tabla.clear()
        self.contenedor_seleccion.set_visibility(False)
        self.contenedor_porcentajes.set_visibility(False)
        self.resultado_separacion.set_visibility(False)
        self.contenedor_preprocesado.set_visibility(False)
        self.contenedor_grafico.clear()
        self.contenedor_grafico.set_visibility(False)
        self.boton_crear_modelo.set_visibility(False)
        self.contenedor_modelo.set_visibility(True)
        self.etiqueta_modelo.set_content("Modelo cargado correctamente.")
        self._mostrar_informacion_modelo()
        self.resultado_modelo.set_visibility(True)
        self.etiqueta_ruta.set_content(
            "Modelo cargado: " + escape(str(ruta)) if ruta else "Modelo cargado"
        )

    def actualizar_descripcion_modelo(self, evento):
        """Actualiza la descripción opcional del modelo."""
        if self.datos_modelo is not None:
            actualizar_descripcion(self.datos_modelo, evento.value or "")

    def ocultar_modelo(self):
        """Oculta el botón y borra el modelo anterior.

        Returns
        -------
        None.
        """
        self.modelo = None
        self.metricas = None
        self.modelo = None
        self.datos_modelo = None
        self._modelo_guardado = False
        self._descripcion_guardada = ""
        self.ruta_modelo = None
        self.entrada_descripcion_modelo.value = ""
        self.entrada_descripcion_modelo.update()
        self.boton_crear_modelo.set_visibility(True)
        self.resultado_modelo.set_visibility(False)
        self.contenedor_modelo.set_visibility(False)

    def mostrar_boton_modelo(self):
        """Muestra el botón para crear un modelo nuevo, sin resultados anteriores.

        Returns
        -------
        None.
        """
        self.ocultar_modelo()
        self.contenedor_modelo.set_visibility(True)
        self.boton_crear_modelo.set_visibility(True)

    def elegir_ruta_guardado(self):
        """Abre el diálogo de guardado y pide confirmación si el archivo ya existe.

        Returns
        -------
        str
            Ruta elegida, con la extensión .model.json añadida, o una cadena
            vacía si el usuario cierra el diálogo o no quiere sobrescribir.
        """
        raiz = tk.Tk()
        raiz.withdraw()
        raiz.attributes("-topmost", True)
        raiz.update()

        try:
            ruta = filedialog.asksaveasfilename(
                title="Guardar modelo",
                defaultextension=EXTENSION,
                filetypes=(("Modelos de Diamond Dogs", "*" + EXTENSION),),
                confirmoverwrite=False,
                initialdir=str(self.ruta_modelo.parent) if self.ruta_modelo else "",
                initialfile=self.ruta_modelo.name if self.ruta_modelo else "",
            )
            if not ruta:
                return ""

            ruta = agregar_extension(ruta)
            if existe_archivo(ruta):
                sobrescribir = messagebox.askyesno(
                    "Sobrescribir archivo",
                    f"El archivo ya existe:\n{ruta}\n\n¿Quieres sobrescribirlo?",
                    parent=raiz,
                )
                if not sobrescribir:
                    return ""
            return str(ruta)
        finally:
            raiz.update()
            raiz.destroy()

    def guardar_modelo_archivo(self):
        """Pide dónde guardar el modelo y lo guarda en un archivo.

        Returns
        -------
        None.
        """
        if self.datos_modelo is None:
            return

        if not self.datos_modelo["descripcion"].strip():
            raiz = tk.Tk()
            raiz.withdraw()
            raiz.attributes("-topmost", True)
            raiz.update()
            
            continuar_sin_desc = messagebox.askyesno(
                "Advertencia: Descripción vacía",
                "El modelo no tiene descripción.\n\n¿Quieres continuar sin descripción?", parent=raiz)
            raiz.update()
            raiz.destroy()
            
            if not continuar_sin_desc:
                return

        ruta = self.elegir_ruta_guardado()
        if not ruta:
            return

        try:
            ruta_guardada = guardar_modelo(ruta, self.datos_modelo)
        except ValueError as e:
            ui.notify(str(e), type="negative", position="center", timeout=5000)
            return
        except Exception as e:
            ui.notify(f"No se pudo guardar el modelo: {e}", type="negative",
                      position="center", timeout=5000)
            return

        ui.notify(f"Modelo guardado en: {ruta_guardada}", type="positive",
                  position="center", timeout=5000)
        self._modelo_guardado = True
        self._descripcion_guardada = self.datos_modelo["descripcion"]
        self.ruta_modelo = Path(ruta_guardada).resolve()

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