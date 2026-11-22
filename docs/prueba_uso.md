# Prueba de usabilidad

## Objetivo

Comprobar que una persona ajena al equipo de desarrollo puede operar la aplicación de principio a fin **siguiendo únicamente las instrucciones del `README.md`**, sin recibir asistencia externa, para completar el flujo completo de trabajo:

1. Cargar un dataset.
2. Crear un modelo (selección de columnas, separación y preprocesado).
3. Guardar el modelo generado en disco.
4. Cargar un modelo previamente guardado.
5. Modificar su descripción y conservar los cambios.
6. Realizar una predicción con los datos introducidos.

## Metodología y desarrollo de la prueba

La evaluación se realizó entregando únicamente el archivo `README.md` junto con el conjunto de datos de ejemplo (`housing.csv`), siguiendo estas pautas:

- **Autonomía total:** La persona usuaria ejecutó las seis tareas del flujo guiándose exclusivamente por la documentación proporcionada en el manual, sin intervención ni aclaraciones por parte del equipo.
- **Observación directa:** Se monitorizó la interacción con la interfaz para comprobar la claridad de los pasos, la comprensión de los controles y la respuesta visual del sistema ante cada acción.

## Comportamiento general observado

El desarrollo de la prueba transcurrió con total normalidad y fluidez. La persona participante logró completar satisfactoriamente las seis tareas propuestas de manera autónoma, siguiendo de forma lineal y natural la guía paso a paso detallada en el `README.md`:

- **Carga y preparación de datos:** El proceso de importar el dataset, visualizarlo en la tabla, seleccionar las variables de entrada y salida, configurar la separación de entrenamiento/test y aplicar una estrategia de limpieza de valores nulos resultó intuitivo gracias a la habilitación progresiva de los pasos en la interfaz.
- **Creación y gestión de modelos:** Tras entrenar el modelo y revisar su fórmula, métricas y gráfico, el guardado en formato `.model.json` y su posterior recuperación mediante el botón de carga funcionaron sin fricciones. La edición de la descripción y el aviso de cambios pendientes quedaron claros en todo momento.
- **Predicción:** Una vez disponible el modelo, la introducción de valores en los campos generados dinámicamente y la obtención del resultado de la predicción se realizaron al primer intento y sin confusiones.

Durante el recorrido por el flujo principal de la aplicación no se detectaron bloqueos críticos ni errores de funcionamiento que impidieran completar las tareas. 

## Conclusiones

La prueba confirma que la aplicación es perfectamente utilizable de forma autónoma por un usuario externo apoyándose únicamente en el `README.md`. La estructura secuencial de la interfaz —que mantiene visibles los pasos pero deshabilita aquellos que aún no pueden ejecutarse— guía de manera muy efectiva al usuario, evita errores de secuencia y facilita la comprensión del ciclo completo de trabajo, desde la carga inicial de datos hasta la obtención de predicciones.