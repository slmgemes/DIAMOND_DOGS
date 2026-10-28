from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine



class ImportadorDatos:
    """Clase para validar y leer archivos de datos en diferentes formatos.

    Attributes
    ----------
    ruta : str
        Ruta del archivo que se va a importar.
    extensiones_validas : set[str]
        Extensiones de archivo admitidas.
    manejadores : dict[str, callable]
        Funciones encargadas de leer cada formato de archivo.

    Methods
    -------
    verificar_existencia()
        Verifica si la ruta especificada existe en el sistema.
    verificar_extension()
        Verifica si la extensión del archivo está soportada.
    leer_csv()
        Lee un archivo CSV.
    leer_excel()
        Lee un archivo de Excel.
    leer_sqlite()
        Lee una base de datos SQLite existente.
    importar()
        Valida el archivo y ejecuta la importación según su formato.
    """


    def __init__(self, ruta: str) -> None:
        """Asigna atributos al objeto.

        Parameters
        ----------
        ruta : Path
            Ruta del archivo que se va a importar.

        Returns
        -------
        None.
        """
        self.ruta = ruta
        self.extensiones_validas = {".csv", ".xlsx", ".xls", ".sqlite", ".db"}

        # Diccionario de despacho integrado en el estado de la clase.
        # Asocia cada extensión con el método encargado de leer el archivo.
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
        """Verifica si la ruta especificada existe en el sistema.

        Raises
        ------
        FileNotFoundError
            Si el archivo no existe.
        """
        if not self.ruta.exists():
            raise FileNotFoundError(f"El archivo no existe: {self.ruta}")


    def verificar_extension(self) -> str:
        """Verifica si la extensión del archivo está soportada.

        Returns
        -------
        str
            Extensión del archivo en minúsculas.

        Raises
        ------
        ValueError
            Si la extensión no está soportada.
        """
        ext = self.ruta.suffix.lower()
        if ext not in self.extensiones_validas:
            raise ValueError(f"Extensión no soportada: {ext}")
        return ext


    def leer_csv(self) -> pd.DataFrame:
        """Lee un archivo CSV.

        Returns
        -------
        pd.DataFrame
            Datos contenidos en el archivo CSV.

        Raises
        ------
        ValueError
            Si el archivo está dañado o no se puede leer.
        """
        try:
            return pd.read_csv(self.ruta)
        except pd.errors.EmptyDataError as e:
            raise ValueError("El archivo CSV no contiene datos (está vacío).") from e
        except Exception as e:
            raise ValueError(f"El archivo CSV está dañado o no se puede leer: {e}")


    def leer_excel(self) -> pd.DataFrame:
        """Lee un archivo de Excel (.xlsx o .xls).

        Returns
        -------
        pd.DataFrame
            Datos contenidos en el archivo Excel.

        Raises
        ------
        ValueError
            Si el archivo está dañado o no se puede leer.
        """
        try:
            return pd.read_excel(self.ruta)
        except Exception as e:
            raise ValueError(f"El archivo Excel está dañado o no se puede leer: {e}")


    def leer_sqlite(self) -> pd.DataFrame:
        """Lee una base SQLite existente y devuelve su primera tabla.

        Returns
        -------
        pd.DataFrame
            Datos contenidos en la tabla de la base de datos.

        Raises
        ------
        ValueError
            Si la base de datos no contiene tablas, contiene varias
            tablas o no se puede leer.
        """
        try:
            con = f"sqlite:///{self.ruta.resolve()}"
            engine=create_engine(con)
            with engine.connect() as conexion:
                tablas = pd.read_sql_query(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name NOT LIKE 'sqlite_%'",
                    conexion,
                )["name"].tolist()

                if not tablas:
                    raise ValueError("La base de datos no contiene tablas.")

                if len(tablas) > 1:
                    raise ValueError(f"La base de datos contiene {len(tablas)} tablas (se esperaba exactamente una).")

                return pd.read_sql_query(f'SELECT * FROM "{tablas[0]}"', conexion)
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"El archivo SQLite está dañado o no se puede leer: {e}")



    def importar(self) ->(tuple[pd.DataFrame, str]):
        """Valida la existencia, la extensión y ejecuta la importación según el formato.

        Returns
        -------
        tuple[pd.DataFrame, str]
            DataFrame con los datos importados y extensión del archivo.

        Raises
        ------
        FileNotFoundError
            Si el archivo no existe.
        ValueError
            Si la extensión no está soportada, no hay un manejador
            definido o el archivo no contiene datos.
        """
        self.verificar_existencia()
        ext = self.verificar_extension()

        # Buscamos la función directamente en el diccionario del objeto.
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

if __name__ == "__main__":

    #primero pasamos el archivo a la clase importador con la ruta del archivo a importar
    importador = ImportadorDatos("datos.csv")

    #luego ejecutamos el proceso de importación: 
    # ---Se valida que la ruta exista y que la extensión esté soportada.
    # ---Se lee el contenido y se valida que el archivo no esté vacío.
    # ---Devuelve el DataFrame en bruto y su extensión.
    df_crudo,ext = importador.importar()