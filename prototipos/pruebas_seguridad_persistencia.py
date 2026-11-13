import json
import os
import tempfile
import pickle
from sklearn.linear_model import LinearRegression
import numpy as np


with tempfile.TemporaryDirectory() as CARPETA:

    #INTENTO CON PICKLE
    class Ataque:
        def __reduce__(self):
            return (print, (" Código ejecutado al cargar el archivo pickle",))


    print("1) PICKLE")
    ruta_pkl = os.path.join(CARPETA, "ataque.pkl")
    with open(ruta_pkl, "wb") as f:
        pickle.dump(Ataque(), f)
    print("  Archivo guardado. Cargando con pickle.load()...")
    with open(ruta_pkl, "rb") as f:
        pickle.load(f)

    #INTENTO CON JSON
    contenido_malicioso = {
        "datos1": [2.0, -1.5],
        "datos2": 3.0,
        "__reduce__": ["print", "Código ejecutado al cargar el archivo json"],
        "description": "__import__('os').system('echo EJECUTADO')",
    }

    print("\n2) JSON")
    ruta_json = os.path.join(CARPETA, "ataque.json")
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(contenido_malicioso, f)
    print("  Archivo guardado. Cargando con json.load()...")
    with open(ruta_json, encoding="utf-8") as f:
        datos = json.load(f)

    print("  No se ha ejecutado nada. Lo cargado son solo datos inertes:")
    for clave, valor in datos.items():
        print(f"    {clave!r}: {valor!r}  ({type(valor).__name__})")

    # 3) LIMITACIÓN DE JSON CON OBJETOS DE MODELO
    print("\n3) JSON - Limitación: no guarda el objeto del modelo directamente")
    
    modelo_ejemplo = LinearRegression()
    modelo_ejemplo.coef_ = np.array([[2.5, -1.0]])
    modelo_ejemplo.intercept_ = np.array([10.0])

    ruta_modelo_fallido = os.path.join(CARPETA, "modelo_fallido.json")
    
    try:
        with open(ruta_modelo_fallido, "w", encoding="utf-8") as f:
            json.dump(modelo_ejemplo, f)
    except TypeError as e:
        print("Demostración del fallo al intentar serializar el objeto directamente:")
        print(f"     TypeError: {e}")