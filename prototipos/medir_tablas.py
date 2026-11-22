import json
import time
from pathlib import Path

from diamond_dogs.importador import ImportadorDatos
from diamond_dogs.tabla_datos import preparar_tabla

ARCHIVO = Path(__file__).parent.parent / "data" / "housing.csv"


def medir(nombre, funcion):
    """Ejecuta la función, mide el tiempo y el tamaño de lo que se enviaría a la tabla."""
    inicio = time.perf_counter()
    datos = funcion()
    segundos = time.perf_counter() - inicio
    megabytes = len(json.dumps(datos)) / 1_000_000
    print(f"{nombre}: {segundos * 1000:.0f} ms | {megabytes:.2f} MB enviados a la tabla")


def main():
    inicio = time.perf_counter()
    df, _ = ImportadorDatos(ARCHIVO).importar()
    print(f"Importar {ARCHIVO.name}: {(time.perf_counter() - inicio) * 1000:.0f} ms "
          f"({len(df)} filas, {len(df.columns)} columnas)")

    medir("Antes  (todo a texto)", lambda: df.astype(str).fillna("").to_dict("records"))
    medir("Después (preparar_tabla)", lambda: preparar_tabla(df))


if __name__ == "__main__":
    main()
