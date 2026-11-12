# COMO CONTRIBUIR

## 1. USO DEL REPOSITORIO

  -Prohibición de subir ciertos archivos: Queda estrictamente prohibido incluir o hacer `commit` de la carpeta data/, los 
  -Datos de los tests: Los datos de las pruebas deben definirse directamente en el código de la prueba como variables  o utilizar un archivo temporal que se eliminará al finalizar.

## 2. RAMAS


-main: Contiene exclusivamente código estable y listo, solo recibe cambios de dev cuando se va a publicar una release.
-dev: Es la rama principal de integración del desarrollo diario que funciona.
¡NO HACER COMMITS DIRECTAMENTE EN MAIN O DEV!
-Ramas feature: Ramas de trabajo de los desarrolladores, tiene que funcionar antes de hacer merge de dev con ellas (pruebas en local y última ejecución de GitHub Actions correctas, ver sección 6.3)
-Ramas fix: Ramas que se utilizan para solucionar cualquier error que pueda tener el proyecto.
-Ramas docs: Utilizadas cuando se cambia la documentación del proyecto.

  ### Nombres:
  Las ramas feature deben utilizar el prefijo del tipo de rama seguidas del numero de la tarea o historia a la que pertenecen y una breve descripción en minúsculas separada por guiones.

  Las ramas fix deben utilizar el prefijo del tipo de rama seguidas del numero de la tarea en la que están arreglando (si pertenece a una en específico) y una breve en minúsculas separada por guiones.
  
  Las ramas docs llevaran de prefijo el tipo de rama seguido por una breve descripción.


## 3. TRABAJO CON LAS RAMAS

  ### 1. Crear una nueva rama de trabajo:
    -Posicionarse en dev y actualizar con lo que hay en el repositorio:

      ```bash
      git checkout dev
      git pull origin dev
      ```

    -Crear nueva rama saliendo de dev:

      ```bash
      git checkout -b <feature/numero-nombre-de-tu-tarea>
      ```

  ### 2. Actualizar tu rama de trabajo:
    -Posicionarte en tu rama de trabajo:

      ```bash
      git checkout <feature/nombre-de-tu-tarea>
      ```

    -Conseguir los cambios de dev y fusionarlos:

      ```bash
      git fetch origin
      git merge origin/dev
      ```
    
  ### 3. Subir tu rama:
    -Hacer un commit de tu rama y subirlo al repositorio:

      ```bash
      git add . (escoge todos los archivos, en caso de que quieras un archivo en específico escribir el nombre)
      git commit -m "escribe el mensaje del commit"
      git push origin <tipo-de-rama/numero-y/o-descripcion>
      ```

    -Al hacer push, GitHub Actions ejecuta las pruebas automáticamente sobre tu rama. Comprueba en la pestaña Actions del repositorio que la última ejecución de tu rama ha terminado correctamente (✔ verde). Si falla, corrígelo y vuelve a subir.
    
    -Actualiza tu rama

    -Si las pruebas pasan en local y la última ejecución de GitHub Actions de tu rama es correcta, fusiónala a dev y súbela al repositorio (reglas completas en la sección 6.3):

      ```bash
      git checkout dev
      git merge <tipo-de-rama/numero-y/o-descripcion>
      git push origin dev
      ```

    -Tras subir dev, comprueba en la pestaña Actions que la ejecución sobre dev también termina correctamente (ver sección 6.3).

  ### 4. Borrar tu rama(cuando acabes una tarea/historia):
    -Una vez dev se haya fusionado y subido al repositorio borra tu rama local:

      ```bash
      git branch -d <tipo-de-rama/numero-y/o-descripcion>
      ```
    
    -Bórrala también en el repositorio:

      ```bash
      git push origin --delete <feature/numero-descripcion>
      ```

## 4. MENSAJES DE LOS COMMIT

tipo: descripción breve en presente o imperativo

  -Posibles tipos de commmits:
    feat: Nueva funcionalidad para el usuario.
    fix: Corrección de un error en el código.
    docs: Cambios únicamente en la documentación.
    test: Añadir o corregir pruebas automatizadas.
    refactor: Cambios en el código que no corrigen errores ni añaden funcionalidades (refactorización).

## 5. PROCEDIMIENTO PARA AÑADIR O ACTUALIZAR DEPENDENCIAS:

  ###1. Añadir una dependencia:

    ```bash
    uv add nombre-paquete
    ```
  
  ### 2. Añadir una dependencia de desarrollo:

    ```bash
    uv add --dev nombre-paquete
    ```

  ### 3. Eliminar una dependencia:

    ```bash
    uv remove nombre-paquete
    ```

  ### 4. Sincronizar entorno:

    ```bash
    uv sync
    ```

## 6. PRUEBAS AUTOMATIZADAS Y REGLAS DE FUSIÓN

  ### 1. Ejecución de las pruebas
    Para ejecutar el conjunto de pruebas del proyecto desde la raíz del repositorio:

    ```bash
    uv run pytest
    ```

    Además, GitHub Actions ejecuta estas mismas pruebas automáticamente, en un entorno limpio, 
    cada vez que se suben cambios a cualquier rama (flujo definido en .github/workflows/tests.yml).
    El resultado de cada ejecución se consulta en la pestaña Actions del repositorio.
    Qué hace cada paso del flujo, cómo localizar la rama y la prueba que ha fallado
    y los fallos que pasan en local pero fallan en GitHub están documentados en docs/integracion-continua.md.

  ### 2. Cómo añadir pruebas nuevas
    Ubicación y formato: Las pruebas se deben crear en la carpeta tests/ con el nombre test_<modulo>.py 
    Cada función de prueba debe empezar por test_ (ej. def test_codigo_a_probar:).

    Importaciones: Se debe importar el código desde el paquete creado con uv init --package que es diamond_dogs.

    Datos sin archivos en el repositorio: Está prohibido subir archivos a la carpeta data/ para realizar pruebas. 
    Los datos se deben definir directamente en el código del test usando variables 
    o mediante el uso de carpetas temporales usando tmp_path de pytest, 
    la cual elimina los archivos creados automáticamente al terminar la prueba.

    Uso de `tmp_path`: Cuando una funcion test necesita crear o modificar archivos, 
    se pasa `tmp_path` como argumento a la función test. 
    Esto genera una carpeta temporal única en el sistema que `pytest` borra automáticamente al finalizar la ejecución.

  ### 3. Cuáles son las reglas de fusión
    Estas reglas se basan en el resultado de GitHub Actions además de en las pruebas en local.

    Rama de trabajo → dev:
    Antes de fusionar cualquier rama de trabajo (feature, fix o docs) en dev, 
    se debe actualizar la rama con los últimos cambios de dev. 
    La fusión solo se autoriza si se cumplen las dos condiciones:
      -Las pruebas pasan en local mediante uv run pytest (el 100 % de los tests con éxito).
      -La última ejecución de GitHub Actions sobre esa rama ha terminado correctamente.

    Después de fusionar en dev:
    Tras cada fusión en dev, se comprueba que la ejecución de GitHub Actions sobre dev 
    también termina correctamente. Si falla:
      -Se crea en Taiga una tarea de corrección.
      -Se corrige en su rama fix.
      -No se fusiona ninguna otra rama en dev hasta que la corrección esté fusionada y dev vuelva a estar en verde.

    dev → main:
    dev solo se fusiona en main si su última ejecución en GitHub Actions ha terminado correctamente.

## 7. PROCEDIMIENTO DE RELEASE

Para publicar una nueva versión del proyecto, se debe seguir estrictamente este procedimiento en orden:

### 1. Asegurarse de que todas las pruebas automatizadas pasan correctamente en la rama `dev`, tanto en local como en GitHub Actions (la última ejecución sobre dev debe estar en verde):

    ```bash
    uv run pytest
    ```
### 2. Situarse en la rama dev y actualizarla con el repositorio remoto:

    ```bash
    git checkout dev
    git pull origin dev
    ```
### 3. Comprobar que el campo version del archivo pyproject.toml refleja exactamente la versión que se va a publicar:

    Si no es así, corregirlo en una rama de trabajo y fusionarlo antes de continuar.

### 4. Fusión de dev en main y subida al repositorio:

    ```bash
    git checkout main
    git pull origin main
    git merge dev
    git push origin main
    ```
### 5. Creación y subida de la etiqueta (Tag) (Por ejemplo la versión 0.1.0):

    ```bash
    git tag -a v0.1.0 -m "Versión 0.1.0"
    git push origin v0.1.0
    ```
### 6. Creación de la Release en GitHub:

    -Acceder a la sección Releases del repositorio en GitHub.
    -Hacer clic en Draft a new release y seleccionar la etiqueta recién subida.
    -Indicar como título de la release el nombre de la versión.
    -Redactar las notas de la release incluyendo:
        Una descripción breve de la aplicación y el estado actual del proyecto.
        Las funcionalidades incluidas (agrupadas a partir de los commits feat) y las correcciones (fix).
        Las funcionalidades pendientes para próximas versiones (como la persistencia de modelos y predicciones).
        Un enlace directo al README.md de la versión publicada (ej. https://github.com/slmgemes/DIAMOND_DOGS/blob/v0.1.0/README.md).
    -Marcar la casilla Set as a pre-release en caso de que aún se encuentre en fase de desarrollo.
    -Publicar la Release haciendo clic en el botón Publish release.
  
  ### 7. Comprobación de la descarga del código fuente:
    -Descargar el archivo comprimido del código fuente.
    -Descomprimirlo en una carpeta nueva y limpia en el equipo local.
    -Comprobar que funciona siguiendo los pasos descritos en el README.md.
