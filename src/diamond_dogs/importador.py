from pathlib import Path
import pandas as pd


class ImportadorDatos:
    """Clase para validar y leer archivos de datos en diferentes formatos."""

    def __init__(self, ruta: str) -> None:
        self._ruta = Path(ruta)
        self._extensiones_validas = {".csv", ".xlsx", ".xls", ".sqlite", ".db"}
        
        # Diccionario de despacho integrado en el estado de la clase
        self._manejadores = {
            ".csv": self.leer_csv,
            ".xlsx": self.leer_excel,
            ".xls": self.leer_excel,
            ".sqlite": self.leer_sqlite,
            ".db": self.leer_sqlite,
        }

    @property
    def ruta(self) -> Path:
        return self._ruta
    @ruta.setter
    def ruta(self, nueva_ruta: str) -> None:
        self._ruta = Path(nueva_ruta)

    @property
    def extensiones_validas(self) -> set[str]:
        return self._extensiones_validas
    @extensiones_validas.setter
    def extensiones_validas(self, nuevas_extensiones: set[str]) -> None:
        self._extensiones_validas = nuevas_extensiones

    @property
    def manejadores(self) -> dict[str, callable]:
        return self._manejadores
    @manejadores.setter
    def manejadores(self, nuevos_manejadores: dict[str, callable]) -> None:
        self._manejadores = nuevos_manejadores

    
    def verificar_existencia(self) -> None:
        """Verifica si la ruta especificada existe en el sistema."""
        if not self.ruta.exists():
            raise FileNotFoundError(f"El archivo no existe: {self.ruta}")


    def verificar_extension(self) -> str:
        """Verifica si la extensión del archivo está soportada."""
        ext = self.ruta.suffix.lower()
        if ext not in self.extensiones_validas:
            raise ValueError(f"Extensión no soportada: {ext}")
        return ext


    def leer_csv(self) -> pd.DataFrame:
        """Lee un archivo CSV."""
        try:
            return pd.read_csv(self.ruta)
        except Exception as e:
            raise ValueError(f"El archivo CSV está dañado o no se puede leer: {e}")


    def leer_excel(self) -> pd.DataFrame:
        """Lee un archivo de Excel (.xlsx o .xls)."""
        try:
            return pd.read_excel(self.ruta)
        except Exception as e:
            raise ValueError(f"El archivo Excel está dañado o no se puede leer: {e}")


    def leer_sqlite(self) -> pd.DataFrame:
        """Parte de Ander:Cuando termine su Cafe despues del break"""

        
        raise NotImplementedError("Lectura de SQLite pendiente de implementar")



    def importar(self) ->(tuple[pd.DataFrame, str]):
        """Valida la existencia, la extensión y ejecuta la importación según el formato."""
        self.verificar_existencia()
        ext = self.verificar_extension()

        # Buscamos la función directamente en el diccionario del objeto
        funcion_lectura = self._manejadores.get(ext)
        if not funcion_lectura:
            raise ValueError(f"No hay un manejador definido para la extensión: {ext}")

        df = funcion_lectura()
        if df.empty:
            raise ValueError("El archivo cargado no contiene datos (está vacío).")

        return (df,ext)



class ProcesadorDatos:
    """Clase modular para procesar y validar datos de archivos"""

    def __init__(self, df: pd.DataFrame, extension: str) -> None:
        self._df = df
        self._extension = extension

        # Diccionario de manejadores para el procesamiento
        self._manejadores_procesamiento: dict[str, callable] = {
            ".csv": self.procesar_csv,
            ".xlsx": self.procesar_excel,
            ".xls": self.procesar_excel,
            ".sqlite": self.procesar_sqlite,
            ".db": self.procesar_sqlite,
        }

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @df.setter
    def df(self, nuevo_df: pd.DataFrame) -> None:
        self._df = nuevo_df

    @property
    def extension(self) -> str:
        return self._extension

    @extension.setter
    def extension(self, nueva_extension: str) -> None:
        self._extension = nueva_extension.lower()

    @property
    def manejadores_procesamiento(self) -> dict[str, callable]:
        return self._manejadores_procesamiento
    @manejadores_procesamiento.setter
    def manejadores_procesamiento(self, nuevos_manejadores: dict[str, callable])-> None:
        self._manejadores_procesamiento = nuevos_manejadores

    def procesar_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def procesar_excel(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def procesar_sqlite(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def procesar(self) -> pd.DataFrame:
        """Selecciona el manejador de procesamiento adecuado según la extensión."""
        if self._df.empty:
            raise ValueError("No hay datos para procesar (el DataFrame está vacío).")
        funcion_procesamiento = self.manejadores_procesamiento.get(self._extension)
        
        # Ejecuta la función correspondiente pasándole el DataFrame
        return funcion_procesamiento(self.df)

#primero pasamos el archivo a la clase importador para guardar información de la ruta y extensión del archivo
importador = ImportadorDatos("datos.csv")

#segundo,verificamos la existencia del archivo y la extensión,y devolvemos el DataFrame y la extensión del archivo
df_crudo,ext = importador.importar()

#tercero, pasamos el DataFrame y la extensión a la clase procesador para validar los datos y manejar errores
procesador = ProcesadorDatos(df_crudo, ext)

# cuarto, procesas los datos del archivo para manejar errores y comprobar la validez de los datos
df_limpio = procesador.procesar()