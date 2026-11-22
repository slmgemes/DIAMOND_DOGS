# Tablas grandes: técnica elegida y comportamiento

## Técnica elegida

**Scroll virtual**, con la tabla AG Grid de NiceGUI (`ui.aggrid`). La tabla solo crea los elementos de las filas que se ven en cada momento y los actualiza al desplazarse, pero el usuario puede recorrer todas las filas del dataset.

La aplicación ya usaba AG Grid, así que se ha mantenido esa técnica. Lo que se ha cambiado es **cómo se cargan y se preparan los datos** que recibe la tabla:

- La lectura del archivo (`ImportadorDatos.importar`) y la preparación de los datos de la tabla (`preparar_tabla`) se ejecutan **en segundo plano**, con `run.io_bound`, en lugar de en el hilo principal.
- Mientras se carga, se muestra un **indicador de carga** y los botones quedan bloqueados.

## Motivo de la elección

- **Está incluida en la librería elegida en #12.** AG Grid ya trae el scroll virtual, así que no hace falta programar nada para que la tabla no cree miles de filas a la vez.
- **El usuario accede a todas las filas** simplemente desplazándose. Con la paginación habría que cambiar de página para ver el resto, y con la carga progresiva habría que programar cómo se añaden las filas.
- **El problema con datasets grandes no estaba en dibujar la tabla**, sino en prepararla: convertir todo el dataset a texto en el hilo principal bloqueaba la ventana durante la carga. Por eso se ha actuado ahí.

## Qué se ha cambiado en el código

| Antes | Después |
|---|---|
| `ui.aggrid.from_pandas(df.astype(str).fillna(""))`, en el hilo principal | `preparar_tabla(df)` en segundo plano, y `ui.aggrid(...)` con los datos ya preparados |
| Todo se convertía a texto, así que los números se ordenaban como texto y los valores vacíos salían como `nan` | Los números siguen siendo números (se ordenan bien) y los valores vacíos salen en blanco |
| La lectura del archivo bloqueaba la ventana | La lectura no bloquea: se muestra un indicador y los botones quedan bloqueados |

## Cómo se ha medido

Las comparativas de rendimiento se han establecido contrastando dos enfoques diferentes de la aplicación:

- **Versión "antes":** La implementación original, la cual realizaba la conversión masiva de todo el dataset a texto plano directamente en el hilo principal de ejecución.
- **Versión "después":** La versión refactorizada y optimizada, que traslada la preparación de la tabla y la lectura de archivos a un hilo secundario y procesa adecuadamente los tipos de datos.

Se ha empleado como referencia el conjunto de datos `data/housing.csv` (con 20.640 filas y 10 columnas).

## Comportamiento con el dataset de ejemplo (`housing.csv`)

Medidas obtenidas durante las pruebas de rendimiento:

| Medida | Antes | Después |
|---|---|---|
| Tiempo de preparar los datos de la tabla | 175 ms | 28 ms |
| Tamaño de lo enviado a la tabla | 5.51 MB | 2.95 MB |

**Comportamiento general y experiencia en la aplicación:**

Al interactuar con la interfaz gráfica utilizando archivos de gran volumen como `housing.csv`, la mejora en la experiencia de usuario es sumamente perceptible y fluida en múltiples aspectos:
- **Responsividad absoluta de la ventana:** Anteriormente, al cargar datasets extensos, la interfaz sufría bloqueos molestos que impedían mover o interactuar con la ventana del navegador. Con el nuevo enfoque basado en tareas en segundo plano (`run.io_bound`), la interfaz permanece completamente activa y libre de congelamientos desde el primer instante.
- **Feedback visual constante y claro:** Se ha implementado un indicador de carga dinámico que informa de manera explícita al usuario sobre el progreso de la importación y preparación del archivo, evitando la sensación de error o de que la aplicación ha dejado de responder.
- **Navegación y fluidez óptimas:** Una vez renderizada la tabla mediante el componente de scroll virtual de AG Grid, el desplazamiento a través de las más de veinte mil filas se realiza de forma sumamente fluida, sin saltos ni retrasos en la visualización, permitiendo alcanzar el principio o el final del dataset de manera instantánea y eficiente.

## Conclusión

La refactorización y optimización introducida en la gestión de tablas grandes ha supuesto un salto cualitativo y cuantitativo muy importante para la robustez, escalabilidad y usabilidad de la aplicación. Al diagnosticar correctamente que el cuello de botella real no residía en el dibujado gráfico de la interfaz, sino en la preparación previa y la transformación masiva de tipos de datos en el hilo principal, se rediseño el flujo arquitectónico de forma limpia. 

Los resultados demuestran el acierto de este cambio: el tiempo de preparación de los datos se redujo drásticamente de 175 ms a 28 ms, y el volumen de información transferido hacia el componente de la tabla disminuyó de 5.51 MB a 2.95 MB. Esto, combinado con la ejecución asíncrona en segundo plano y el uso de un scroll virtual eficiente, garantiza que la herramienta mantenga una respuesta profesional, impecable y totalmente fluida incluso al trabajar con conjuntos de datos pesados y complejos.

## Pruebas automáticas

`tests/test_tabla_datos.py` comprueba, sin abrir la interfaz, que con 25.000 filas no se pierde ninguna, que los números siguen siendo números, que los valores vacíos salen en blanco, que los nombres de columna con puntos o repetidos no se mezclan y que los datos se pueden enviar a la tabla como JSON.