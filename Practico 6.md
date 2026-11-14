<div align="center">

# Consigna Practica 6
## Analisis estatico de codigo

**Universidad Catolica del Uruguay - Facultad de Ingenieria**

<br>

**Asignatura:** Desarrollo de Software Seguro <br>
**Profesores:** Wiler Alvez / Alejandro Piccardo <br>
**Estudiante:** Martin Mujica <br>
**Fecha:** 14/11/2026

</div>

<br>
<br>

## Herramienta seleccionada

La herramienta seleccionada es **Semgrep**, una herramienta de analisis estatico de codigo fuente. Se utiliza para identificar patrones de programación potencialmente inseguros, errores y desviaciones de las prácticas definidas mediante reglas.

Semgrep permite incorporar controles de seguridad durante el desarrollo, antes de desplegar el software. Puede ejecutarse desde la terminal y automatizarse dentro de un proceso de integración continua. 

## ¿Cómo funciona Semgrep?

### Selección de los archivos que se analizarán

El análisis comienza con la identificación de los archivos incluidos en el alcance del escaneo. Semgrep reconoce lenguajes compatibles y considera las exclusiones configuradas. La extensión de un archivo, las reglas seleccionadas y la configuración de exclusiones influyen en lo que efectivamente se analiza.

### Interpretación de la estructura del código

Para los lenguajes con soporte, Semgrep interpreta el código mediante representaciones como los **árboles de sintaxis abstracta (AST)**. Un AST representa elementos del programa, como llamadas a funciones, expresiones y asignaciones. Esto permite buscar estructuras de programación en lugar de limitarse a coincidencias literales de texto.

### Aplicación de reglas

Las reglas establecen qué situaciones debe buscar la herramienta. Entre sus componentes se encuentran:

| Componente | Función |
| --- | --- |
| id | Identifica la regla. |
| languages | Establece los lenguajes a los que se aplica. |
| message | Explica el hallazgo. |
| severity | Indica la severidad asignada por la regla. |
| Patrones u operadores de análisis | Definen las condiciones que deben cumplirse para generar una coincidencia. |
| metadata, cuando existe | Agrega información, como referencias o clasificaciones de seguridad. |

La detección depende de las reglas efectivamente ejecutadas. Una vulnerabilidad puede quedar fuera del resultado si ninguna regla seleccionada representa el comportamiento que la produce.

### Generación y revisión de los resultados

Cuando el código cumple las condiciones de una regla, Semgrep produce un hallazgo. Los resultados permiten ubicar el archivo y las líneas involucradas, identificar la regla y consultar su explicación.

La severidad indicada permite organizar la revisión, pero no demuestra por sí sola la explotabilidad ni el impacto real en la aplicación. Cada hallazgo debe contrastarse con el contexto del código y, una revision humana.

## Community Edition y Semgrep

| Herramienta | Qué representa |
| --- | --- |
| **Semgrep Community Edition** | Motor comunitario de análisis y herramientas asociadas, utilizable localmente con reglas comunitarias o propias. |
| **Semgrep Code con motor Pro** | Producto SAST que incorpora capacidades de análisis más profundas y acceso a reglas Pro según la configuración y los permisos disponibles. |

## Limitaciones específicas de Community Edition

### Menor alcance del seguimiento de datos

El análisis de flujo de CE como intraprocedimental: sigue las interacciones dentro de una función o método. Semgrep Code agrega análisis interprocedimental, entre funciones, y permite habilitar análisis entre archivos en los lenguajes compatibles.

Esto puede resultar relevante cuando una aplicación distribuye la recepción de datos, su validación y su utilización entre varios componentes. CE puede identificar patrones locales, pero perder la relación completa entre ellos. Esta limitación no significa que CE solamente pueda escanear un archivo por ejecución: puede analizar muchos archivos, aunque no siga el flujo de datos entre ellos.

### Diferencias en las reglas disponibles

Community Edition puede utilizar reglas comunitarias y reglas propias. Las reglas Pro constituyen un conjunto propietario adicional mantenido por el equipo de investigación de Semgrep, orientado a ampliar la cobertura y producir hallazgos útiles. No forman parte del conjunto comunitario básico. 

## Limitaciones que también afectan a otras versiones

Las diferencias anteriores no eliminan las limitaciones generales del análisis estático. Tanto CE como Pro pueden producir:

- **Falsos positivos**
- **Falsos negativos**

La ausencia de hallazgos no demuestra que una aplicación sea segura. Un análisis puede omitir problemas por sus reglas, su alcance o las características del código. Los errores de análisis y las exclusiones también deben revisarse antes de interpretar los resultados.

Además, una herramienta no determina automáticamente todos los requisitos de la aplicacion ni confirma el comportamiento de la aplicación en funcionamiento. Por eso, sus resultados deben complementarse con revisión y pruebas. Las capacidades Pro pueden aportar más contexto, pero no garantizan detectar todas las vulnerabilidades.

## Procedimiento para ejecutar los escaneos

**Preparacion de las carpetas y de la imagen**

```powershell
$codigo = (Get-Location).Path
$reportes = Join-Path $codigo "reports"
```

$codigo identifica la carpeta del repositorio y $reportes la carpeta de salida. Los reportes se escriben en /reports.

**Community Edition en main**

```powershell
git switch main

docker run --rm `
    -v "${codigo}:/src:ro" `
    -v "${reportes}:/reports" `
    -w /src `
    $sgImage `
    sh -c 'semgrep scan --oss-only --config auto --exclude reports --max-lines-per-finding 0 --json-output /reports/ce-main.json --text-output /reports/ce-main.txt . > /reports/ce-main.log 2>&1; sg_rc=$?; cat /reports/ce-main.log; exit $sg_rc'
```

**Community Edition en practico-2**

```powershell
git switch practico-2

docker run --rm `
    -v "${codigo}:/src:ro" `
    -v "${reportes}:/reports" `
    -w /src `
    $sgImage `
    sh -c 'semgrep scan --oss-only --config auto --exclude reports --max-lines-per-finding 0 --json-output /reports/ce-practico-2.json --text-output /reports/ce-practico-2.txt . > /reports/ce-practico-2.log 2>&1; sg_rc=$?; cat /reports/ce-practico-2.log; exit $sg_rc'
```

`--oss-only` fuerza el motor comunitario y `--config auto` obtiene reglas seleccionadas automaticamente para el proyecto. `--exclude reports` evita analizar la carpeta de resultados. El punto final indica que se analiza el directorio de trabajo `/src`, respetando las exclusiones de Semgrep.

**Preparacion del token para Pro**

Para ejecutar Pro se necesita acceso habilitado a Semgrep Code y un token Agent/CI.

```powershell
$tokenSeguro = Read-Host "Token de Semgrep Agent (CI)" -AsSecureString
$env:SEMGREP_APP_TOKEN = ([PSCredential]::new("semgrep", $tokenSeguro)).GetNetworkCredential().Password
```

**Pro en main**

```powershell
git switch main

docker run --rm `
    -e SEMGREP_APP_TOKEN `
    -v "${codigo}:/src:ro" `
    -v "${reportes}:/reports" `
    -w /src `
    $sgImage `
    sh -c 'semgrep ci --code --pro --no-suppress-errors --exclude reports --dataflow-traces --max-lines-per-finding 0 --json-output /reports/pro-main.json --text-output /reports/pro-main.txt > /reports/pro-main.log 2>&1; sg_rc=$?; cat /reports/pro-main.log; exit $sg_rc'
```

**Pro en practico-2**

```powershell
git switch practico-2

docker run --rm `
    -e SEMGREP_APP_TOKEN `
    -v "${codigo}:/src:ro" `
    -v "${reportes}:/reports" `
    -w /src `
    $sgImage `
    sh -c 'semgrep ci --code --pro --no-suppress-errors --exclude reports --dataflow-traces --max-lines-per-finding 0 --json-output /reports/pro-practico-2.json --text-output /reports/pro-practico-2.txt > /reports/pro-practico-2.log 2>&1; sg_rc=$?; cat /reports/pro-practico-2.log; exit $sg_rc'
```

`--code` selecciona el producto SAST y `--pro` solicita el motor avanzado. `--dataflow-traces` agrega recorridos de datos a la salida de texto cuando existen. `--no-suppress-errors` evita ocultar los errores de ejecucion mediante la supresion predeterminada de CI.

Los parametros `--json-output` y `--text-output` guardan los resultados. La redireccion `> ... 2>&1` guarda la salida del comando en el log. Finalmente, `cat` muestra ese registro y `exit $sg_rc` conserva el codigo de salida de Semgrep.

**JSON con formato legible**

Se utilizo una IA para reformatear los archivos JSON y facilitar su lectura. Se mantuvieron los mismos datos y hallazgos de los reportes originales.

## Archivos obtenidos y utilidad de cada uno

Por cada combinacion de version y rama se generaron tres archivos principales: JSON, TXT y LOG.

| Formato | Que contiene |
| --- | --- |
| `.json` | Hallazgos estructurados: archivo, regla, mensaje, severidad, CWE y clasificacion OWASP cuando existe. |
| `.txt` | Explicacion de la alerta y fragmentos de codigo. En Pro incluye recorridos de datos en los hallazgos que los tienen. | 
| `.log` | Registro de la ejecucion: motor, reglas, archivos analizados, exclusiones, advertencias, resumen y, en estas ejecuciones, tambien hallazgos. |
| `-legible.json` | El mismo contenido del JSON original, con sangrias y saltos para facilitar su lectura. |

## Hallazgos entre `main` y `practico-2`

### Community Edition

| Archivo | Hallazgo reportado | CWE | `main` | `practico-2` |
| --- | --- | --- | --- | --- |
| `Ejercicio1/Dockerfile` | Dockerfile sin instrucción USER para ejecutar con un usuario sin privilegios. | CWE-250 | 12 | 12 |
| `Ejercicio2/Dockerfile` | Dockerfile sin instrucción USER para ejecutar con un usuario sin privilegios. | CWE-250 | 12 | 12 |
| `Ejercicio3/src/main/resources/templates/upload.html` | Formulario POST de carga de afiches sin token CSRF explícito en la plantilla. | CWE-352 | 39–46 | 39–46 |
| `Ejercicio4/src/main/java/com/cinebuscador/config/SpelEvaluator.java` | Evaluación dinámica de SpEL en evaluate(String expression). | CWE-94 | 14–34 | 14–34 |
| `Ejercicio5/src/main/java/com/cinebuscador/config/EncryptionService.java` | Uso de AES en modo ECB reportado en Cipher.getInstance(...), línea 50. | CWE-327 | 50 | Sin alerta |
| `Ejercicio5/src/main/java/com/cinebuscador/config/EncryptionService.java` | Uso de AES en modo ECB reportado en Cipher.getInstance(...), línea 64. | CWE-327 | 64 | Sin alerta |
| `Ejercicio5/src/main/resources/templates/index.html` | Formulario POST de inicio de sesión (/login) sin token CSRF explícito en la plantilla.| CWE-352 | 45–51 | 45–51 |
| `Ejercicio5/src/main/resources/templates/index.html` | Formulario POST de registro (/register) sin token CSRF explícito en la plantilla.| CWE-352 | 56–64 | 56–64 |
| **Total de alertas** |  |  | **8** | **6** |

### Pro

| Archivo | Hallazgo reportado | CWE | `main` | `practico-2` |
| --- | --- | --- | --- | --- |
| `Ejercicio1/Dockerfile` | Dockerfile sin instrucción USER para ejecutar con un usuario sin privilegios. | CWE-250 | 12 | 12 |
| `Ejercicio1/app.py` | Inyección SQL en buscar_funciones. El reporte de practico-2 sigue el dato de ordenamiento hasta la consulta. | CWE-89 | 32 | 41 |
| `Ejercicio2/Dockerfile` | Dockerfile sin instrucción USER para ejecutar con un usuario sin privilegios. | CWE-250 | 12 | 12 |
| `Ejercicio2/app.py` | Inyección SQL en la búsqueda. | CWE-89 | 35 | 35 |
| `Ejercicio3/src/main/resources/templates/upload.html` | Formulario POST de carga de afiches sin token CSRF explícito en la plantilla. | CWE-352 | 39–46 | 39–46 |
| `Ejercicio4/src/main/java/com/cinebuscador/config/SpelEvaluator.java` | Evaluación dinámica de SpEL en evaluate(String expression). | CWE-94 | 14–34 | 14–34 |
| `Ejercicio4/src/main/java/com/cinebuscador/config/SpelEvaluator.java` | Entrada HTTP buscar que llega a parseExpression. La traza registra el flujo desde FuncionController.java. | CWE-95 | 30 | Sin alerta |
| `Ejercicio5/src/main/java/com/cinebuscador/config/EncryptionService.java` | Uso de AES en modo ECB reportado en Cipher.getInstance(...), línea 50. | CWE-327 | 50 | Sin alerta |
| `Ejercicio5/src/main/java/com/cinebuscador/config/EncryptionService.java` | Uso de AES en modo ECB reportado en Cipher.getInstance(...), línea 64. | CWE-327 | 64 | Sin alerta |
| `Ejercicio5/src/main/resources/templates/index.html` | Formulario POST de inicio de sesión (/login) sin token CSRF explícito en la plantilla. | CWE-352 | 45–51 | 45–51 |
| `Ejercicio5/src/main/resources/templates/index.html` | Formulario POST de registro (/register) sin token CSRF explícito en la plantilla. | CWE-352 | 56–64 | 56–64 |
| **Total de alertas** |  |  | **11** | **8** |

### Diferencias entre CE y Pro

| Comparación | `main` | `practico-2` |
| --- | --- | --- |
| Presentes en CE y Pro | 8 | 6 |
| Exclusivas de Pro | 3 | 2 |
| Exclusivas de CE | 0 | 0 |


## Falsos positivos en practico-2

### Ejercicio 1 - Inyeccion SQL

**Archivo:** `Ejercicio1/app.py`  
**Detectado por:** Semgrep Pro.

La alerta es un falso positivo porque el texto que escribe el usuario se pasa como un parametro separado de la consulta. Ademas, la columna de ordenamiento se elige entre dos opciones fijas y la direccion se limita a `ASC` o `DESC`. Con esos controles, la entrada del usuario se usa para buscar y ordenar sin cambiar la estructura de la consulta SQL.

### Ejercicio 4 - Inyeccion mediante SpEL

**Archivo:** `SpelEvaluator.java`  
**Detectado por:** Semgrep CE y Pro.

La alerta es un falso positivo. Semgrep encuentra el metodo que evalua expresiones, pero la llamada desde el controlador esta comentada. Ahora la busqueda compara el texto ingresado con los nombres de las funciones. Por eso, en ese flujo, la entrada del usuario nunca llega al evaluador.

## Falsos negativos en main

### Ejercicio 1 - Inyección SQL

**Archivo** `Ejercicio1/app.py`, líneas 29–32.  
**Omitido por** Semgrep Community Edition.  
**Detectado por** Semgrep Pro, línea 32.

En main, el buscador incorpora el texto de búsqueda y el sentido del orden directamente en la consulta SQL. CE omitió esa inyección. Pro sí la detectó en la llamada a db.execute(sql).

En practico-2, la búsqueda se pasa como parámetro y el orden se limita a valores permitidos. Pro siguió marcando la consulta en la línea 41, por lo que esa alerta es un falso positivo en la rama corregida.

### Ejercicio 2 - XSS almacenado

**Archivo** `Ejercicio2/templates/edit.html`, línea 86.  
**Omitido por** Semgrep Community Edition y Pro.

En main, la aplicación guarda la descripción de la película y luego la muestra en la vista de edición con safe. Ese filtro desactiva el escape de HTML, por lo que el navegador puede interpretar el contenido guardado como código. En practico-2 se quitó el filtro y Jinja volvió a escapar la descripción.


## Analisis estatico con un LLM
### Prompt utilizado

> Realizá un análisis estático de seguridad del repositorio [https://github.com/msmujica/DSS-Practico2-MartinMujica.git](https://github.com/msmujica/DSS-Practico2-MartinMujica.git), revisando las ramas main y practico-2.
>
> Revisá el código fuente y la configuración de los ejercicios. Basá cada hallazgo en evidencia concreta del repositorio y presentá los resultados por rama.
>
> Para cada hallazgo, indicá:
>
> - **Archivo y función o sección** donde aparece.
> - **Problema de seguridad**.
> - **Impacto** y condiciones necesarias para que ocurra.
> - **CWE**, cuando corresponda.
>
> Entregá los resultados en Markdown, con una tabla para `main` y otra para `practico-2`.

### Hallazgos de GPT en `main`

| ID | Ejercicio | Hallazgo reportado | CWE |
| --- | --- | --- | --- |
| M01 | 1 | Inyeccion SQL en la consulta de busqueda. | CWE-89 |
| M02 | 2 | Inyeccion SQL en la consulta de busqueda. | CWE-89 |
| M03 | 2 | XSS almacenado en la vista previa de la descripcion. | CWE-79 |
| M04 | 2 | Edicion de peliculas sin verificar permisos en el servidor. | CWE-862 |
| M05 | 1 y 2 | Flask arranca con el modo debug activo por defecto. | CWE-489 |
| M06 | 3 | Posible escritura fuera de la carpeta de afiches al guardar con el nombre original. | CWE-22 |
| M07 | 3 | Posible lectura fuera de la carpeta de afiches, segun la configuracion. | CWE-22 |
| M08 | 3 | Carga de archivos sin validar su tipo ni contenido. | CWE-434 |
| M09 | 3 | Cambio de afiches sin verificar permisos en el servidor. | CWE-862 |
| M10 | 3 | Los afiches anteriores se acumulan al reemplazarlos. | CWE-770 |
| M11 | 3 | Posible problema en la version de Tomcat que procesa las cargas de archivos. | CWE-770 |
| M12 | 4 | La busqueda evalua el texto del usuario como una expresion SpEL. | CWE-917 |
| M13 | 5 | Las contraseñas se guardan con cifrado reversible AES-ECB. | CWE-257, CWE-327 |
| M14 | 5 | La clave de cifrado esta fija en el codigo. | CWE-321 |
| M15 | 5 | El valor cifrado de la contraseña se muestra en la respuesta HTML del login. | CWE-522 |
| M16 | 5 | El codigo del login carece de un limite de intentos. | CWE-307 |
| M17 | 5 | El servidor permite registrar contraseñas sin una longitud minima. | CWE-521 |
| M18 | 5 | El mensaje de registro permite distinguir si un usuario ya existe. | CWE-204 |
| M19 | 5 | El despliegue incluido puede enviar credenciales por HTTP. | CWE-319 |
| M20 | 5 | Posibles nombres de usuario duplicados en registros simultaneos, segun el esquema de la base. | CWE-367 |

### Hallazgos de GPT en `practico-2`

| ID | Ejercicio | Hallazgo reportado | CWE |
| --- | --- | --- | --- |
| P01 | 1 y 2 | Flask sigue arrancando con el modo debug activo por defecto. | CWE-489 |
| P02 | 2 | La inyeccion SQL sigue presente en la consulta de busqueda. | CWE-89 |
| P03 | 2 | La edicion de peliculas sigue sin verificar permisos en el servidor. | CWE-862 |
| P04 | 3 | La carga de afiches revisa la extension, pero falta verificar que el contenido sea una imagen valida. | CWE-434 |
| P05 | 3 | Sigue pendiente verificar que la lectura quede dentro de la carpeta de afiches. | CWE-22 |
| P06 | 3 | El cambio de afiches sigue sin verificar permisos en el servidor. | CWE-862 |
| P07 | 3 | Los afiches anteriores se siguen acumulando al reemplazarlos. | CWE-770 |
| P08 | 3 | Se mantiene la observacion sobre la version de Tomcat que procesa las cargas de archivos. | CWE-770 |
| P09 | 5 | Un posible problema con la version de BCrypt y el manejo de contraseñas largas. | CWE-287, CWE-521 |
| P10 | 5 | El codigo del login sigue sin limitar los intentos. | CWE-307 |
| P11 | 5 | El servidor sigue permitiendo contraseñas sin una longitud minima. | CWE-521 |
| P12 | 5 | El registro sigue indicando si un usuario ya existe. | CWE-204 |
| P13 | 5 | El despliegue incluido sigue permitiendo el envio de credenciales por HTTP. | CWE-319 |
| P14 | 5 | Sigue la posibilidad de usuarios duplicados en registros simultaneos, segun el esquema de la base. | CWE-367 |

### Comparacion con Semgrep

| Analisis | `main` | `practico-2` |
| --- | ---: | ---: |
| Semgrep CE | 8 alertas | 6 alertas |
| Semgrep Pro | 11 alertas | 8 alertas |
| GPT | 20 hallazgos y observaciones | 14 hallazgos y observaciones |

GPT reporto mas puntos porque tambien reviso cosas como los permisos, la configuracion y las dependencias. Por ejemplo, encontro el XSS del Ejercicio 2 en main y el modo debug de Flask en ambas ramas. Esos puntos no aparecieron en los reportes de Semgrep. Algunos dependen de la configuracion o de la version que se use al ejecutar la aplicacion, asi que los conteos representan lo que reporto cada analisis.

Tambien hubo coincidencias, GPT y Semgrep Pro encontraron la inyeccion SQL del Ejercicio 2 en ambas ramas. Para el Ejercicio 1, GPT vio que la consulta ya estaba corregida en practico-2, lo que coincide con la revision del falso positivo de Pro. Por otro lado, CE y Pro marcaron los contenedores que corren como root en los Ejercicios 1 y 2 y GPT no incluyo ese punto.