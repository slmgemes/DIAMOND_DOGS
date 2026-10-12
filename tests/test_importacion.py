from pathlib import Path
import pandas as pd
import sqlite3
import pytest

from diamond_dogs.importador import ImportadorDatos

def test_archivo_no_existe():
    """Comprueba que lanza FileNotFoundError si la ruta no existe."""
    importador = ImportadorDatos("archivo_falso_que_no_existe.csv")
    with pytest.raises(FileNotFoundError):
        importador.importar()

def test_extension_no_soportada(tmp_path):
    """Comprueba que lanza ValueError si la extensión no está permitida."""
    archivo_txt = tmp_path / "datos.txt"
    archivo_txt.write_text("archivo de prueba con extensión incorrecta")
    
    importador = ImportadorDatos(archivo_txt)
    with pytest.raises(ValueError, match="no soportada"):
        importador.importar()

def test_importar_csv_exitoso(tmp_path):
    """Comprueba que un CSV válido se importa correctamente."""
    archivo_csv = tmp_path / "datos.csv"
    archivo_csv.write_text("tipos,nombre\n1,csv\n2,excel\n3,sql")
    
    importador = ImportadorDatos(archivo_csv)
    df, ext = importador.importar()
    
    assert ext == ".csv"
    assert not df.empty
    assert len(df) == 3
    assert list(df.columns) == ["tipos", "nombre"]

def test_archivo_vacio(tmp_path):
    """Comprueba que lanza ValueError si el archivo no contiene datos."""
    archivo_vacio = tmp_path / "vacio.csv"
    archivo_vacio.write_text("tipos,nombre\n")
    
    importador = ImportadorDatos(archivo_vacio)
    with pytest.raises(ValueError, match="no contiene datos"):
        importador.importar()

def test_importar_excel_exitoso(tmp_path):
    """Comprueba que un archivo Excel válido se importa correctamente."""
    archivo_excel = tmp_path / "datos.xlsx"
    
    df_original = pd.DataFrame({"tipos": [1, 2, 3], "nombre": ["csv", "excel", "sql"]})
    df_original.to_excel(archivo_excel, index=False)
    
    importador = ImportadorDatos(archivo_excel)
    df, ext = importador.importar()
    
    assert ext in [".xlsx", ".xls"]
    assert not df.empty
    assert len(df) == 3
    assert list(df.columns) == ["tipos", "nombre"]


def test_excel_dañado(tmp_path):
    """Comprueba que lanza ValueError si el archivo Excel está dañado o malformado."""
    archivo_corrupto = tmp_path / "corrupto.xlsx"
    archivo_corrupto.write_text("esto no es un excel válido, es texto plano")
    
    importador = ImportadorDatos(archivo_corrupto)
    with pytest.raises(ValueError, match="no se puede leer"):
        importador.importar()

def test_sqli_alida(tmp_path):
    """Comprueba que una base de datos SQLite con exactamente una tabla se importa correctamente."""
    db_path = tmp_path / "correcta.db"
    
    conexion = sqlite3.connect(db_path)
    conexion.execute("CREATE TABLE extensiones (tipos INT, nombre TEXT);")
    conexion.execute("INSERT INTO extensiones VALUES (1, 'sql');")
    conexion.commit()
    conexion.close()
    
    importador = ImportadorDatos(db_path)
    df, ext = importador.importar()
    
    assert ext in [".sqlite", ".db"]
    assert not df.empty
    assert len(df) == 1
    assert list(df.columns) == ["tipos", "nombre"]

def test_sql_notablas(tmp_path):
    """Comprueba que lanza ValueError si la base de datos SQLite no contiene ninguna tabla."""
    db_path = tmp_path / "vacia.db"
    
    conexion = sqlite3.connect(db_path)
    conexion.close()
    
    importador = ImportadorDatos(db_path)
    with pytest.raises(ValueError, match="no contiene tabla"):
        importador.importar()

def test_sql_multiples(tmp_path):
    """Comprueba que lanza ValueError si la base de datos SQLite contiene más de una tabla."""
    db_path = tmp_path / "multiples.db"
    
    # Creamos una base de datos con dos tablas
    conexion = sqlite3.connect(db_path)
    conexion.execute("CREATE TABLE tabla1 (tipos INT);")
    conexion.execute("CREATE TABLE tabla2 (tipos INT);")
    conexion.commit()
    conexion.close()
    
    importador = ImportadorDatos(db_path)
    with pytest.raises(ValueError, match="contiene"):
        importador.importar()


def test_sql_dañada(tmp_path):
    """Comprueba que lanza ValueError si el archivo SQLite está dañado o malformado."""
    db_path = tmp_path / "corrupta.db"
    
    # Escribimos texto plano simulando un archivo SQLite corrupto
    db_path.write_text("esto no es una base de datos sqlite válida")
    
    importador = ImportadorDatos(db_path)
    with pytest.raises(ValueError, match="dañado o no se puede leer"):
        importador.importar()

def test_archivos_locales_():
    """Comprueba la importación y la estructura de los datasets de ejemplo
    ubicados en la carpeta local data/, validando que no estén vacíos
    y que mantengan las extensiones y tipos correctos.
    """
    carpeta_data = Path("data")
    
    if not carpeta_data.exists():
        pytest.skip("La carpeta data/ no existe en el entorno local.")

    extensiones_validas = {".csv", ".xlsx", ".xls", ".sqlite", ".db"}
    archivos = []

    for f in carpeta_data.iterdir():
        if (f.is_file()) and (f.suffix.lower() in extensiones_validas):
            archivos.append(f)

    if not archivos:
        pytest.skip("No se encontraron archivos compatibles en la carpeta data/.")

    for archivo in archivos:
        importador = ImportadorDatos(archivo)
        df, ext = importador.importar()
        
        assert not df.empty
        assert ext in extensiones_validas
        assert len(df.columns) > 0