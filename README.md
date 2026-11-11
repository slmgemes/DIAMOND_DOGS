PRÁCTICA INGENIERÍA DE SOFTWARE(LUNES)

Este proyecto consiste en el desarrollo de una aplicación en Python para el procesamiento, análisis y modelado de datos. Su objetivo es proporcionar una interfaz interactiva que permita el acceder a los modelos de regresión lineal y múltiple (que se pueden almacenar para acceder a ellos de manera posterior), evaluar sus resultados y hacer predicciones en base a ellos.

FUNCIONALIDADES INCLUIDAS

Esta versión incluye la carga y preparación de datos y la creación y evaluación del modelo:
- Importación de datos: Soporte para archivos CSV, Excel (.xlsx, .xls) y bases de datos SQLite (.sqlite, .db).
- Visualización: Tabla integrada para la inspección rápida de los datos importados.
- Selección de columnas: Elección de variables de entrada (features) y de salida (target).
- Separación de datos: División configurable en conjuntos de entrenamiento y test mediante porcentajes y semillas de reproducibilidad.
- Preprocesamiento de valores nulos: Detección automática de celdas vacías y aplicación de estrategias (eliminación de filas, imputación por media, mediana o valor constante numérico) de forma no destructiva, permitiendo cambiar de método libremente sin alterar el archivo original en disco.
- Creación del modelo: Entrenamiento de un modelo de regresión lineal (simple o múltiple) únicamente con el conjunto de entrenamiento. El botón "Crear modelo" solo aparece cuando se han confirmado las columnas, se han separado los datos y no quedan valores inexistentes.
- Fórmula del modelo: Se muestra con los nombres de las columnas seleccionadas y los coeficientes redondeados a 4 decimales.
- Métricas de evaluación: Coeficiente de determinación (R²) y error cuadrático medio (ECM), calculados en entrenamiento y en test y mostrados en una tabla.
- Gráfico del ajuste: Integrado en la aplicación. En regresión simple muestra los puntos de entrenamiento y test junto con la recta del modelo; en regresión múltiple, los valores reales frente a los predichos junto con la recta en la que ambos coinciden.

REQUISITOS

    -Python >= 3.12
    -uv: Administrador de paquetes y entornos virtuales de Python. En caso de no tenerlo instalado:
        -- [Windows] Ejecuta en Powershell:
            powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        -- [macOS y Linux]:
            curl -LsSf https://astral.sh/uv/install.sh | sh

            o

            wget -qO- https://astral.sh/uv/install.sh | sh


INSTALAR ENTORNO

1. Clona el repositorio e ingresa a la carpeta del proyecto:

   git clone <URL_DEL_REPOSITORIO>
   cd DIAMOND_DOGS

2. Instala el entorno y todos lo que requiere la aplicación:

    uv sync

3. Ejecuta la aplicación:

    uv run python src/diamond_dogs/interfaz.py

EJECUTAR APLICACIÓN

1. Instala el entorno escribiendo en la terminal:
    
    uv sync

2. Ejecuta la aplicación ejecutando en la terminal:

    uv run python src/diamond_dogs/interfaz.py

3. Interactúa con el botón de selección de archivos para cargar un dataset.

4. Selecciona las columnas de entrada y salida correspondientes y confirma la selección.

5. Introduce el porcentaje de test deseado junto con la semilla y pulsa separar datos.

6. En el bloque de tratamiento de valores inexistentes, escoge una estrategia de preprocesado y aplícala; el sistema permite reintentar y cambiar de opción cuantas veces sea necesario partiendo siempre de los datos originales intactos.

7. Cuando no queden valores inexistentes, pulsa "Crear modelo" para entrenar el modelo y consultar su fórmula, sus métricas (R² y ECM) y el gráfico del ajuste.