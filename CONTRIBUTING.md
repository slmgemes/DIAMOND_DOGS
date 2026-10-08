#COMO CONTRIBUIR

##1. USO DEL REPOSITORIO

  -Prohibición de subir ciertos archivos: Queda estrictamente prohibido incluir o hacer `commit` de la carpeta data/, los 
  -Datos de los tests: Los datos de las pruebas deben definirse directamente en el código de la prueba como variables  o utilizar un archivo temporal que se eliminará al fianlizar.

##2. RAMAS


-main: Contiene exclusivamente código estable y listo, solo recibe cambios de dev cuando se va a publicar una release.
-dev: Es la rama principal de integración del desarrollo diario que funciona.
¡NO HACER COMMITS DIRECTAMENTE EN MAIN O DEV!
-Ramas feature: Ramas de trabajo de los desarrolladores, tiene que funcionar antes de hacer merge de dev con ellas
-Ramas fix: Ramas que se utilizan para solucionar cualquier error que pueda tener el proyecto.
-Ramas docs: Utilizadas cuando se cambia la documentación del proyecto.

  ###2.1. Nombres:
  Las ramas feature deben utilizar el prefijo del tipo de rama seguids del numero de rama y una breve en minúsculas separada por guiones.

  Las ramas fix y docs llevaran de prefijo el tipo de rama seguido por una breve descripción.


##3. TRABAJO CON LAS RAMAS

  ###1. Crear una nueva rama de trabajo:
    -Posicionarse en dev y actualizar con lo que hay en el repositorio:
      ```bash
      git checkout dev
      git pull origin dev

    -Crear nueva rama saliendo de dev:
      ```bash
      git checkout -b <feature/nombre-de-tu-tarea>

  ###2. Actualizar tu rama de trabajo:
    -Posicionarte en tu rama de trabajo:
      ```bash
      git checkout <feature/nombre-de-tu-tarea>

    -Conseguir los cambios de dev y fusionarlos:
      ```bash
      git fetch origin
      git merge origin/dev
    
  ###3. Subir tu rama:
    -Hacer un commit de tu rama y subirlo al repositorio:
      ```bash
      git add . (escoge todos los archivos, en caso de que quieras un archivo en específico escribir el nombre)
      git commit -m "escribe el mensaje del commit"
      git push origin <tipo-de-rama/numero-y/o-descripcion>
    
    -Actualiza tu rama

    -Si funciona, fusiónala a dev y súbela al repositorio:
      ```bash
      git checkout dev
      git merge <tipo-de-rama/numero-y/o-descripcion>
      git push origin dev

  ###4. Borrar tu rama(cuando acabes una tarea/historia):
    -Una vez dev se haya fusionado y subido al repositorio borra tu rama local:
      ```bash
      git branch -d <tipo-de-rama/numero-y/o-descripcion>
    
    -Bórrala también en el repositorio:
      ```bash
      git push origin --delete <feature/numero-descripcion>

##4. MENSAJES DE LOS COMMIT

tipo: descripción breve en presente o imperativo

  -Posibles tipos de commmits:
    feat: Nueva funcionalidad para el usuario.
    fix: Corrección de un error en el código.
    docs: Cambios únicamente en la documentación.
    test: Añadir o corregir pruebas automatizadas.
    refactor: Cambios en el código que no corrigen errores ni añaden funcionalidades (refactorización).

##5. PROCEDIMIENTO PARA AÑADIR O ACTUALIZAR DEPENDENCIAS:

  ###1. Añadir una dependencia:
    ```bash
    uv add nombre-paquete
  
  ###2. Añadir una dependencia de desarrollo:
    ```bash
    uv add --dev nombre-paquete

  ###3. Eliminar una dependencia:
    ```bash
    uv remove nombre-paquete

  ###4. Sincronizar entorno:
    ```bash
    uv sync

## 6. PRUEBAS AUTOMATIZADAS Y REGLAS DE FUSIÓN

  ### 1. Ejecución de las pruebas
    Para ejecutar el conjunto de pruebas del proyecto desde la raíz del repositorio:
    ```bash
    uv run pytest
    ```

  ### 2. Cómo añadir pruebas nuevas
    Ubicación y formato: Las pruebas se deben crear en la carpeta tests/ con el nombre test_<modulo>.py 
    Cada función de prueba debe empezar por test_ (ej. def test_mi_funcion():).

    Importaciones: Se debe importar el código desde el paquete creado con uv init --package que es diamond_dogs.

    Datos sin archivos en el repositorio: Está prohibido subir archivos a la carpeta data/ para realizar pruebas. 
    Los datos se deben definir directamente en el código del test usando variables 
    o mediante el uso de carpetas temporales usando tmp_path de pytest, 
    la cual elimina los archivos creados automáticamente al terminar la prueba.

    Uso de `tmp_path`: Cuando una funcion test necesita crear o modificar archivos, 
    se pasa `tmp_path` como argumento a la función test. 
    Esto genera una carpeta temporal única en el sistema que `pytest` borra automáticamente al finalizar la ejecución.

  ### 3. Cuáles son las reglas de fusión
    Antes de fusionar cualquier rama de trabajo (feature, fix o docs) en dev, 
    se debe actualizar la rama con los últimos cambios de dev 
    y ejecutar todas las pruebas en local mediante uv run pytest. 
    La fusión solo se autoriza si el 100 % de los tests se ejecutan con éxito.