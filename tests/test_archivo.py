def test_comprobar_fichero_temporal(tmp_path):
    # 1. Se crea la ruta del archivo temporal
    fichero = tmp_path / "datos.txt"
    
    # 2. Se escribe el contenido (por ejemplo, el 5)
    fichero.write_text("5")
    
    # 3. Se lee y comprueba
    assert fichero.read_text() == "5"