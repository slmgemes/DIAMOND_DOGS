from pathlib import Path
import pandas as pd


class ImportadorDatos:
    """Clase modular para la validación e importación de datos desde diferentes formatos."""

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
        return pd.read_csv(self.ruta)


    def leer_excel(self) -> pd.DataFrame:
        """Lee un archivo de Excel (.xlsx o .xls)."""
        return pd.read_excel(self.ruta)


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

        return (funcion_lectura(),ext)