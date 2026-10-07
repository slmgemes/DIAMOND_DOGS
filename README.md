PRÁCTICA INGENIERÍA DE SOFTWARE(LUNES)

Este proyecto consiste en el desarrollo de una aplicación en Python para el procesamiento, análisis y modelado de datos. Su objetivo es proporcionar una interfaz interactiva que permita el acceder a los modelos de regresión lineal y múltiple (que se pueden almacenar para acceder a ellos de manera posterior), evaluar sus resultados y hacer predicciones en base a ellos.

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
    uv run python -m diamond_dogs