# Datos de prueba
Los archivos de datos válidos utilizados en la ejecución de este plan de pruebas no se encuentran almacenados en el repositorio del proyecto. Para la correcta ejecución, quien realice las pruebas debe colocarlos previamente en la carpeta local data/ del proyecto. Los escenarios de error que requieran archivos vacíos o con formatos no válidos no necesitan ficheros previos, ya que los propios pasos de cada caso detallan cómo crearlos de forma local.

## 1. Archivos con datos válidos:

### Dataset CSV (housing.csv)

Formato: CSV delimitado por comas (.csv).

Número de filas y columnas: 20.640 filas y 10 columnas.

Columnas utilizadas en las pruebas:

Entradas (features): median_income, housing_median_age, total_rooms.

Salida (target): median_house_value.

Columnas con valores inexistentes o no numéricos: Contiene valores nulos (NaN) en ciertas celdas de la columna total_bedrooms para probar los casos de preprocesado, y la columna categórica de texto ocean_proximity para verificar las validaciones de tipo no numérico.

### Dataset Excel (housing.xlsx)

Formato: Libro de Microsoft Excel (.xlsx).

Número de filas y columnas: 20.640 filas y 10 columnas.

Columnas utilizadas en las pruebas: Mismas especificaciones y nombres de columnas que el archivo CSV (median_income, housing_median_age, total_rooms como entradas y median_house_value como salida).

Columnas con valores inexistentes o no numéricos: Coincide con la distribución de celdas vacías en total_bedrooms y la columna de texto ocean_proximity.

### Dataset SQLite (housing.sqlite)

Formato: Base de datos SQLite (.sqlite / .db).

Número de filas y columnas: Tabla única con 20.640 filas y 10 columnas.

Columnas utilizadas en las pruebas: Mismas variables e idénticos nombres de columna que en los formatos anteriores.

Columnas con valores inexistentes o no numéricos: Presencia de valores nulos equivalentes en la columna total_bedrooms y texto en ocean_proximity.

# Pruebas

## CP-SEL

### CP-SEL-01. Visualización y disponibilidad de los selectores de columnas
Historia: #11

Objetivo: Comprobar que tras cargar los datos correctamente, los selectores de entrada y salida aparecen y se muestran listos para su uso.

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv (ver sección "Datos de prueba"), situado en la carpeta data/ del proyecto.

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.    

Localizar el selector etiquetado como "Columnas de entrada" y comprobar que permita selección única y múltiple.

Localizar el selector etiquetado como "Columna de salida" y comprobar que es de selección única.

Resultado esperado: Ambos selectores muestran de manera automática todas las columnas disponibles en housing.csv. El selector de entrada permite marcar uno o varios elementos y el de salida solo permite uno.

### CP-SEL-02. Actualización de los selectores al cargar un nuevo dataset
Historia: #11

Objetivo: Verificar que al importar un nuevo archivo, los selectores se limpian y se actualizan con las columnas del nuevo conjunto.

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv y archivo housing.xlsx (ver sección "Datos de prueba"), situados en la carpeta data/ del proyecto.

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.

Seleccionar "Columnas de entrada" y "Columna de salida" y darle al botón "Confirmar selección".

Pulsar el botón "Seleccionar archivo" de nuevo.

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.xlsx.

Observar los selectores "Columnas de entrada" y "Columna de salida" y comprobar que las selecciones anteriores ya no están.

Resultado esperado: Las selecciones anteriores quedan completamente borradas y los selectores muestran exclusivamente las columnas correspondientes al nuevo archivo housing.xlsx.

### CP-SEL-03. Selección válida de múltiples entradas y una salida
Historia: #11

Objetivo: Comprobar que el usuario puede seleccionar varias variables independientes y una dependiente, confirmando con éxito la selección.

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv (ver sección "Datos de prueba"), situado en la carpeta data/ del proyecto; columnas de entrada: median_income y housing_media_age; columna de salida: median_house_value.

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.

En el selector "Columnas de entrada", marcar las casillas correspondientes a median_income y housing_media_age.

En el selector "Columna de salida", elegir la opción median_house_value.

Pulsar el botón "Confirmar selección".

Resultado esperado: Aparece un mensaje de éxito en la interfaz indicando las columnas seleccionadas correctamente, y se habilitan los controles del siguiente paso (separación de datos).

### CP-SEL-04. Modificación libre de la selección previa antes de confirmar
Historia: #11

Objetivo: Verificar que el usuario puede cambiar de opinión y modificar las columnas marcadas las veces que desee antes de pulsar el botón de confirmación.

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv (ver sección "Datos de prueba"), situado en la carpeta data/.

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.

En el selector "Columnas de entrada", marcar temporalmente una columna incorrecta (por ejemplo, total_rooms).

Desmarcar total_rooms y marcar la columna correcta median_income.

Pulsar el botón "Confirmar selección".

Resultado esperado: La aplicación registra únicamente las opciones definitivas (median_income), sin guardar rastro de la selección descartada previa.

### CP-SEL-05. Conflicto por seleccionar la misma columna como entrada y salida
Historia: #11

Objetivo: Comprobar que la aplicación impide utilizar una misma columna simultáneamente como variable predictora y objetivo.

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv (ver sección "Datos de prueba"), situado en la carpeta data/; columna seleccionada en ambos campos: median_income.

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.

En el selector "Columnas de entrada", marcar median_income y otra más (por ejemplo, total_rooms).

En el selector "Columna de salida", elegir la misma columna median_income.

Pulsar el botón "Confirmar selección".

Resultado esperado: Al marcar como columna de salida una columna que ya se eligió como entrada, el programa simplemente borra esa selección de las columnas elegidas como entrada. En este caso, al confirmar la selección, quedará la columa total_rooms de entrada y median_income de salida.

### CP-SEL-06. Intento de confirmación con campos vacíos (Escenario de error)
Historia: #11

Objetivo: Verificar que la interfaz rechaza la confirmación si no se ha escogido al menos una columna de entrada y una de salida.

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv (ver sección "Datos de prueba"), situado en la carpeta data/; ninguna columna seleccionada.

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.

Dejar vacíos los selectores "Columnas de entrada" y "Columna de salida".

Pulsar directamente el botón "Confirmar selección".

Resultado esperado: La aplicación muestra un mensaje de error advirtiendo que falta por seleccionar las columnas obligatorias de entrada o salida, manteniendo bloqueados los pasos posteriores.

### CP-SEL-07. Selección de una columna no numérica como entrada o salida (Escenario de error)
Historia: #11

Objetivo: Comprobar que la aplicación detecta e impide el uso de variables con formato de texto/categórico para el entrenamiento del modelo lineal.

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv (ver sección "Datos de prueba"), situado en la carpeta data/; columna no numérica elegida: ocean_proximity.

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.

En el selector "Columnas de entrada" o "Columna de salida", marcar la columna de texto ocean_proximity.

Pulsar el botón "Confirmar selección".

Resultado esperado: La interfaz muestra un mensaje de error específico indicando que la columna seleccionada no es numérica y por tanto no se puede emplear en el modelo de regresión lineal.

## CP-MOD

### CP-MOD-01. Habilitación correcta del botón "Crear modelo"

Historia: #16

Objetivo: Comprobar que el botón "Crear modelo" permanece deshabilitado hasta que se cumplen todas las precondiciones y se habilita correctamente al completarlas.

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv (ver sección "Datos de prueba"), situado en la carpeta data/.

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.

Seleccionar columnas de entrada y salida válidas y confirmar la selección.

Realizar la separación en conjuntos de entrenamiento y test (con un porcentaje válido entre 1 y 99).

Asegurarse de que no quedan valores inexistentes (aplicando el preprocesado si fuera necesario).

Observar el estado del botón "Crear modelo".

Resultado esperado: El botón "Crear modelo" aparece inicialmente deshabilitado. Se habilita únicamente cuando las columnas están confirmadas, los datos separados y el preprocesado de nulos completado.

### CP-MOD-02. Creación exitosa de un modelo de regresión múltiple y visualización de resultados

Historia: #16

Objetivo: Verificar la creación correcta de un modelo de regresión lineal con varias variables y la visualización de su gráfico de valores reales frente a predichos, fórmula y métricas.

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv (ver sección "Datos de prueba"), situado en la carpeta data/; entradas: "median_income", "housing_median_age"; salida: "median_house_value".

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.

Seleccionar columnas de entrada "median_income" y "housing_median_age" y columna de salida "median_house_value" y confirmar la selección.

Realizar la separación en conjuntos de entrenamiento y test (con un porcentaje válido entre 1 y 99).

Asegurarse de que no quedan valores inexistentes (aplicando el preprocesado si fuera necesario).

Pulsar el botón "Crear modelo".

Comprobar el mensaje de éxito en la interfaz.

Revisar el gráfico de valores reales frente a predichos (verificando la presencia de puntos de entrenamiento y de test diferenciados por color/leyenda y la recta de identidad).

Consultar el bloque de la fórmula del modelo y el panel de métricas ($R^2$ y ECM) para entrenamiento y test.

Resultado esperado: Se muestra un mensaje de éxito indicando que el modelo se ha creado. El gráfico muestra los conjuntos diferenciados con su leyenda y ejes etiquetados como "Valor real" y "Valor predicho". La fórmula se muestra en el formato correcto con los nombres de las columnas y coeficientes redondeados, y se despliegan claramente las métricas $R^2$ y ECM diferenciadas por conjunto.

### CP-MOD-03. Actualización de resultados al crear un nuevo modelo

Historia: #16

Objetivo: Comprobar que al entrenar un nuevo modelo, este sustituye por completo al anterior actualizando el gráfico, la fórmula y las métricas en la interfaz.

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv (ver sección "Datos de prueba"), situado en la carpeta data/; entradas seleccionadas: "median_income","housing_median_age" y salida: "median_house_value"; nueva entrada seleccionada: "total_rooms".

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.

Seleccionar columnas de entrada "median_income" y "housing_median_age" y columna de salida "median_house_value" y confirmar la selección.

Realizar la separación en conjuntos de entrenamiento y test (con un porcentaje válido entre 1 y 99).

Asegurarse de que no quedan valores inexistentes (aplicando el preprocesado si fuera necesario).

Pulsar el botón "Crear modelo".

Revisar el gráfico de valores reales frente a predichos y la fórmula y métricas.

Modificar las columnas de entrada seleccionadas (por ejemplo, cambiar a "total_rooms").

Confirmar selección, separar datos de nuevo y re-preprocesar si es necesario.

Pulsar de nuevo el botón "Crear modelo".

Resultado esperado: La interfaz actualiza de forma inmediata el gráfico de ajuste, la fórmula matemática y las métricas ($R^2$ y ECM), reflejando los resultados del nuevo modelo generado y descartando el anterior.

### CP-MOD-04. Formato correcto de la fórmula con coeficientes negativos

Historia: #16

Objetivo: Verificar que los coeficientes negativos se muestran correctamente restando, sin generar expresiones erróneas del tipo "+ -".

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv (ver sección "Datos de prueba"), situado en la carpeta data/; variables seleccionadas que produzcan un coeficiente negativo (por ejemplo, "housing_median_age" frente a otra variable según los datos).

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.

Seleccionar columna de entrada "housing_median_age" y columna de salida válida(por ejemplo, "median_house_value") y confirmar la selección.

Realizar la separación en conjuntos de entrenamiento y test (con un porcentaje válido entre 1 y 99).

Asegurarse de que no quedan valores inexistentes (aplicando el preprocesado si fuera necesario).

Pulsar el botón "Crear modelo".

Examinar el texto de la fórmula generada en la pantalla.

Resultado esperado: La fórmula muestra los coeficientes negativos precedidos directamente del signo menos (ej. "- <coef_n> * <entrada_n>"), evitando por completo dobles signos como "+ -".

### CP-MOD-05. Creación exitosa de un modelo de regresión simple y visualización de resultados

Historia: #16

Objetivo: Verificar la creación correcta de un modelo de regresión lineal simple (una sola variable) y la visualización de su gráfico de ajuste, fórmula y métricas.

Precondiciones: La aplicación está abierta y no hay ningún dataset cargado.

Datos de prueba: Archivo housing.csv (ver sección "Datos de prueba"), situado en la carpeta data/; entrada: `median_income`; salida: `median_house_value`.

Pasos:

Pulsar el botón "Seleccionar archivo".    

En el explorador de archivos, ir a la carpeta data/ del proyecto y seleccionar housing.csv.

Seleccionar columna de entrada "median_income" y columna de salida válida(por ejemplo, "median_house_value") y confirmar la selección.

Realizar la separación en conjuntos de entrenamiento y test (con un porcentaje válido entre 1 y 99).

Asegurarse de que no quedan valores inexistentes (aplicando el preprocesado si fuera necesario).

Pulsar el botón "Crear modelo".

Comprobar el mensaje de éxito en la interfaz.

Revisar el gráfico integrado en la ventana (verificando que muestra los puntos del conjunto de entrenamiento, los nombres correctos en los ejes, los puntos del conjunto de test diferenciados por color/leyenda y la recta de ajuste del modelo).

Consultar el bloque de la fórmula del modelo (formato: `<salida> = <coef_1> * <entrada_1> + <término_independiente>`) y el panel de métricas ($R^2$ y ECM) para entrenamiento y test.

Resultado esperado: Se muestra un mensaje de éxito indicando que el modelo se ha creado. El gráfico muestra la recta de ajuste junto con los puntos reales de entrenamiento y test diferenciados. La fórmula y las métricas se muestran correctamente diferenciadas por conjunto.