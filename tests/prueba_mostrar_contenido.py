from diamond_dogs.importador import ImportadorDatos


def comprobar_datasets() -> None:
    archivos = [
        "data/housing.csv",
        "data/housing.db",
        "data/housing.xlsx",
    ]

    for archivo in archivos:
        importador = ImportadorDatos(archivo)
        df, extension = importador.importar()

        print("\n" + f" ARCHIVO: {archivo} ".center(160, "="))
        print(f"Extensión: {extension}".center(160))

        print("\n" + " PRIMERAS FILAS ".center(160, "-"))
        print(df.head())

        print("\n" + " TIPOS DE LAS COLUMNAS ".center(30, "-"))
        print(df.dtypes)

        print("\n")


if __name__ == "__main__":
    comprobar_datasets()

