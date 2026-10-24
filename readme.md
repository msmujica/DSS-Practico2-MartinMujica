# Practico 4 - Pruebas de seguridad

## Introduccion
Los ejercicios utilizan las siguientes tecnologias:

| Ejercicio | Vulnerabilidad | Tecnologia de prueba |
| --- | --- | --- |
| 1 | SQL Injection | PyTest |
| 2 | Cross-Site Scripting (XSS) almacenado | PyTest |
| 3 | Carga de archivos sin restricciones | PyTest y requests |
| 4 | Server-Side Template Injection (SpEL) | PyTest y requests |
| 5 | Almacenamiento inseguro de contraseñas | JUnit 5 y Maven |

> Los ejercicios deben levantarse de a uno, ya que los Ejercicios 1 y 2 utilizan el puerto `5000`, mientras que los Ejercicios 3, 4 y 5 utilizan el puerto `8080`. Antes de cambiar de ejercicio se debe ejecutar `docker compose down`.

---

# Ejercicio 1 - SQL Injection

## Vulnerabilidad

**SQL Injection.**

## Pruebas implementadas

### `test_busqueda_injection_or`

Envia el siguiente payload mediante el parametro buscar:

```text
' OR 1=1 --
```

La prueba comprueba que:

- El endpoint responda con codigo HTTP `200`.
- El payload sea interpretado como texto y no como parte de la consulta SQL.
- La busqueda no devuelva ninguna funcion.
- No aparezcan peliculas como `Dune: Parte Dos`, `Godzilla x Kong: El Nuevo Imperio` o `La Sociedad de la Nieve`.

En la version vulnerable, la condicion `OR 1=1` devuelve todas las funciones. En la version corregida, el parametro se envia por separado mediante `LIKE ?` y la cantidad de resultados es `0`.

### `test_busqueda_injection_url`

Realiza una busqueda normal mediante:

```text
buscar=s
```

e intenta modificar el ordenamiento mediante:

```text
sentido=ASC LIMIT 1
```

La prueba comprueba que:

- El endpoint responda con codigo HTTP `200`.
- El valor `ASC LIMIT 1` no agregue un limite a la consulta.
- La busqueda continue devolviendo las `12` funciones correspondientes.

En la version vulnerable solamente se devuelve un resultado. En la version corregida, el valor no permitido se reemplaza por `ASC`.

## Ejecucion

Desde la carpeta `Ejercicio1`:

```bash
docker compose up --build -d
docker compose exec sqli python -m pytest tests/test.py -v -s
```

---

# Ejercicio 2 - Cross-Site Scripting (XSS)

## Vulnerabilidad

**Cross-Site Scripting almacenado.**

## Pruebas implementadas

### `test_descripcion_xss`

Guarda el siguiente payload en la descripcion de una pelicula:

```html
<script>alert('XSS')</script>
```

Despues vuelve a abrir `/edit/1` y comprueba que:

- El payload no aparezca como una etiqueta `<script>` ejecutable.
- Las etiquetas aparezcan escapadas como `&lt;script&gt;` y `&lt;/script&gt;`.

En la version vulnerable, el filtro `safe` hace que el codigo se incorpore directamente al HTML. En la version corregida, Jinja aplica el escape automatico.

## Ejecucion

Desde la carpeta `Ejercicio2`:

```bash
docker compose up --build -d
docker compose exec xss python -m pytest tests/test.py -v -s
```

---

# Ejercicio 3 - Carga de archivos sin restricciones

## Vulnerabilidad

**Carga de archivos sin restricciones y uso predecible del nombre original.**

## Pruebas implementadas

### `test_rechaza_archivo_txt`

Genera un nombre aleatorio y envia un archivo .txt mediante un POST multipart a:

```text
/upload/1
```

La prueba comprueba que:

- La aplicacion regrese al formulario `/upload/1`.
- El archivo rechazado no este disponible mediante `/uploads/{nombre}`.
- El intento de acceso al archivo devuelva `404`.

### `test_acepta_jpg_y_cambia_nombre`

Envia un archivo con extension `.jpg` y un nombre original aleatorio.

La prueba comprueba que:

- La imagen permitida sea aceptada.
- La aplicacion redirija al inicio.
- El archivo no este disponible mediante su nombre original.
- La solicitud a `/uploads/{nombre-original}.jpg` devuelva `404`, demostrando que el servidor utiliza un UUID.

## Ejecucion

Desde la carpeta `Ejercicio3`:

```bash
docker compose up --build -d
docker compose exec cinebuscador3 python -m pytest tests/test.py -v -s
```

---

# Ejercicio 4 - Server-Side Template Injection

## Vulnerabilidad

**Server-Side Template Injection**

## Pruebas implementadas

### `test_expresion_spel_no_se_ejecuta`

Envia la siguiente expresion mediante el parametro buscar:

```text
4*2
```

La prueba comprueba que:

- La aplicacion responda con codigo HTTP 200.
- La expresion no sea evaluada y no aparezca Resultados buscando por: 8.
- La aplicacion trata 4*2 como texto y muestre No se encontraron coincidencias.

### `test_busqueda_normal_funciona`

Envia una busqueda legitima:

```text
aveng
```

La prueba comprueba que:

- La respuesta tenga codigo HTTP 200.
- La aplicacion encuentre y muestre Avengers.

En la version vulnerable, la busqueda se envia a SpelEvaluator: 4*2 se transforma en 8 y una entrada normal como aveng puede producir un error 500. En la version corregida, el valor se utiliza directamente como texto.

## Ejecución

Desde la carpeta `Ejercicio4`:

```bash
docker compose up --build -d
docker compose exec cinebuscador4 python -m pytest tests/test.py -v -s
```

---

# Ejercicio 5 - Almacenamiento inseguro

## Vulnerabilidad

**Almacenamiento inseguro de contraseñas mediante AES con clave estatica y modo ECB.**

## Pruebas implementadas

Las pruebas estan implementadas con JUnit en:

```text
src/test/java/com/cinebuscador/config/EncryptionServiceTest.java
```

### `debeGenerarUnHashBCrypt`

Comprueba que:

- Se genere un valor diferente de la contraseña original.
- El resultado no sea nulo.
- El hash comience con `$2`, identificador utilizado por BCrypt.

### `mismaPasswordDebeGenerarHashesDiferentes`

Genera dos hashes de la misma contraseña y comprueba que sean diferentes. Esto valida la utilizacion de un salt aleatorio por parte de BCrypt.

### `debeVerificarLaPasswordCorrectamente`

Comprueba que:

- La contraseña correcta sea aceptada por `verifyPassword()`.
- Una contraseña diferente sea rechazada.

### `noDebeExistirUnMetodoParaDescifrarPasswords`

Comprueba que `EncryptionService` no exponga un metodo `decrypt()`. Los hashes de contraseñas deben verificarse, pero no deben poder descifrarse.

## Ejecución

Desde la carpeta `Ejercicio5`:

```bash
docker compose up --build -d
docker compose exec cinebuscador5 mvn test
```