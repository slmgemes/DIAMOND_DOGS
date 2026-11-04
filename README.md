PRÁCTICA INGENIERÍA DE SOFTWARE(LUNES)

Este proyecto consiste en el desarrollo de una aplicación en Python para el procesamiento, análisis y modelado de datos. Su objetivo es proporcionar una interfaz interactiva que permita el acceder a los modelos de regresión lineal y múltiple (que se pueden almacenar para acceder a ellos de manera posterior), evaluar sus resultados y hacer predicciones en base a ellos.

FUNCIONALIDADES INCLUIDAS

Esta versión incluye el módulo completo de carga y preparación de datos:
- Importación de datos: Soporte para archivos CSV, Excel (.xlsx, .xls) y bases de datos SQLite (.sqlite, .db).
- Visualización: Tabla integrada para la inspección rápida de los datos importados.
- Selección de columnas: Elección de variables de entrada (features) y de salida (target).
- Separación de datos: División configurable en conjuntos de entrenamiento y test mediante porcentajes y semillas de reproducibilidad.
- Preprocesamiento de valores nulos: Detección automática de celdas vacías y aplicación de estrategias (eliminación de filas, imputación por media, mediana o valor constante numérico) de forma no destructiva, permitiendo cambiar de método libremente sin alterar el archivo original en disco.

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

    uv run python .\src\diamond_dogs\interfaz.py 

VERIFICACIÓN MANUAL DEL FLUJO

1. Ejecuta la aplicación ejecutando en la terminal:

    uv run python .\src\diamond_dogs\interfaz.py 

2. Interactúa con el botón de selección de archivos para cargar un dataset.

3. Selecciona las columnas de entrada y salida correspondientes y confirma la selección.

4. Introduce el porcentaje de test deseado junto con la semilla y pulsa separar datos.

5. En el bloque de tratamiento de valores inexistentes, escoge una estrategia de preprocesado y aplícala; el sistema permite reintentar y cambiar de opción cuantas veces sea necesario partiendo siempre de los datos originales intactos.