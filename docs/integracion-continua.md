# Integración continua con GitHub Actions

## 1. Qué es y cuándo se ejecuta

El archivo `.github/workflows/tests.yml` hace que GitHub ejecute las pruebas
automáticamente en un ordenador limpio (Ubuntu), distinto de los nuestros.

Se ejecuta **cada vez que alguien hace `git push` a cualquier rama**.

## 2. Qué hace cada paso

| Paso | Qué hace | Por qué |
|------|----------|---------|
| Descargar el código | Copia la rama subida a la máquina de GitHub | Probamos solo lo que está en el repositorio |
| Instalar dependencias del sistema | Instala `python3-tk` con apt | `interfaz.py` importa `tkinter`, que en Ubuntu no viene instalado |
| Instalar uv | Instala el gestor de dependencias | Es la herramienta que usa el proyecto |
| Instalar dependencias | Ejecuta `uv sync --locked` | Instala las versiones exactas de `uv.lock`; falla si `uv.lock` no está al día |
| Ejecutar pruebas | Ejecuta `uv run pytest` | Si alguna prueba falla, la ejecución termina en rojo |

## 3. Cómo consultar el resultado de una ejecución

1. En el repositorio de GitHub, abrir la pestaña **Actions**.
2. En la lista hay una fila por ejecución. Cada fila indica el mensaje del
   commit, la **rama** y el estado: ✔ verde (correcto), ✘ rojo (fallo) o
   amarillo (en curso).
3. Para ver el detalle de un fallo: abrir la ejecución → clic en el job `test`
   → abrir el paso marcado en rojo (normalmente "Ejecutar pruebas").
4. En el log de pytest, las líneas `FAILED` o `ERROR` indican **qué prueba**
   ha fallado, y las líneas de encima explican el motivo.

## 4. Fallos que pasan en local pero fallan en GitHub Actions

| Fecha | Prueba | Causa | Cómo se resolvió |
|-------|--------|-------|------------------|
| 2026-11-08 | `tests/test_interfaz.py` | `interfaz.py` importa `tkinter`. En Windows viene con Python, pero en el Ubuntu de GitHub es el paquete aparte `python3-tk`, que no estaba instalado. Error: `ModuleNotFoundError: No module named 'tkinter'` | Añadir al flujo el paso `sudo apt-get install -y python3-tk` antes de instalar las dependencias |