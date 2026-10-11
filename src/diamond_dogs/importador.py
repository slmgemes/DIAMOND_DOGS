from pathlib import Path


def verificar_existencia(ruta: str) -> Path:
    """Verifica si la ruta especificada existe en el sistema."""
    path = Path(ruta)

    if not path.exists():
        raise FileNotFoundError(f"El archivo no existe: {path}")
    return path


def verificar_extension(path: Path) -> str:
    """Verifica si la extensión del archivo está soportada."""
    EXTENSIONES_VALIDAS = {".csv", ".xlsx", ".xls", ".sqlite", ".db"}

    if path.suffix.lower() not in EXTENSIONES_VALIDAS:
        raise ValueError(f"Extensión no soportada: {path.suffix}")

    return path.suffix.lower()


def importar_datos(ruta):
    """Importa los datos desde un archivo."""
    path = verificar_existencia(ruta)
    verificar_extension(path)

