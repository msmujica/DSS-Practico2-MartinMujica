<div align="center">

# Consigna Practica 1 - Creacion de ambiente de trabajo
# Consigna Practica 1
## Creacion de ambiente de trabajo

**Universidad Catolica del Uruguay - Facultad de Ingenieria**

<br>

**Asignatura:** Desarrollo de Software Seguro <br>
**Profesores:** Wiler Alvez / Alejandro Piccardo <br>
**Estudiante:** Martin Mujica <br>
**Fecha:** 05/09/2026

</div>

<br>

## Introduccion

El presente informe documenta el analisis y la mitigacion de diferentes vulnerabilidades de seguridad incluidas intencionalmente en las aplicaciones proporcionadas para el Practico 2.

Para cada ejercicio se busca identificar la vulnerabilidad, comprender su causa, demostrar su explotacion mediante una prueba de concepto (POC) dentro de un entorno local, e implementar una modificacion que elimine o reduzca el riesgo.

Despues de implementar cada mitigacion, se vuelve a ejecutar la aplicacion para comprobar que la aplicacion continue operativa y que las entradas utilizadas durante la POC ya no produzcan el comportamiento vulnerable.

## Herramientas utilizadas

- **Git**
- **Visual Studio Code**
- **Docker**
- **Navegador web**


## Vulnerabilidades analizadas

1. **Ejercicio 1 - Inyeccion SQL (SQL Injection)**
   - `CWE-89`.
2. **Ejercicio 2 - Cross-Site Scripting (XSS)**
   - `CWE-79`.

3. **Ejercicio 3 - Carga de archivos sin restricciones**
   - `CWE-434`.

4. **Ejercicio 4 - Server-Side Template Injection (SSTI)**
   - `CWE-1336`.

5. **Ejercicio 5 - Almacenamiento inseguro**
   - `CWE-922`.

<br>
<br>

---
# Ejercicio 1 - Inyeccion SQL (SQL Injection)

## Marco teorico

Una inyeccion ocurre cuando una aplicacion recibe un dato del usuario y lo coloca directamente dentro de una instruccion. Esto puede provocar que el dato sea interpretado como parte del codigo y no solamente como informacion.

En una inyeccion SQL, el usuario consigue modificar una consulta enviada a la base de datos. Esto sucede normalmente cuando el programa construye el SQL concatenando o interpolando directamente los valores recibidos.

Las entradas vulnerables no provienen solamente de campos de texto. Tambien pueden llegar desde:

- Parametros de la URL.
- Selectores HTML.
- Formularios.
- Cookies.
- Cuerpos JSON.
- Encabezados HTTP.

Por este motivo, el servidor siempre debe validar y manejar de forma segura los datos recibidos, aunque la interfaz limite las opciones disponibles.

### Formas comunes de SQL injection

Algunas formas comunes de aprovechar una SQL injection son:

- Modificar una condicion para obtener mas resultados.
- Ignorar parte de la consulta original.
- Utilizar `UNION SELECT` para consultar otra informacion.
- Consultar las tablas internas de la base de datos.
- Modificar partes como `ORDER BY` o `LIMIT`.

### Elementos utilizados en una inyeccion

**La comilla simple:**

```sql
'
```

puede utilizarse para cerrar un texto dentro de la consulta.

El operador `OR` permite agregar otra condicion:

```sql
OR 1=1
```

La expresion `1=1` siempre es verdadera, por lo que puede conseguir que una consulta devuelva todos los registros.

**Los dos guiones:**

```sql
--
```

indican el comienzo de un comentario en SQL. Todo lo que aparece despues puede ser ignorado por el motor de base de datos.

**La instruccion:**

```sql
UNION SELECT
```

permite agregar un segundo `SELECT` a la consulta original. Para que funcione, ambos `SELECT` deben devolver la misma cantidad de columnas.

<br>

## Prueba de concepto (POC)

Pra las siguientes pruebas primero se comprobo el comportamiento vulnerable y posteriormente se repitieron las pruebas despues de implementar la mitigacion.

### POC 1 - Alteracion de la condicion con `OR 1=1`

Para comprobar la vulnerabilidad del campo de busqueda, se ingreso el siguiente valor:

```text
' OR 1=1 --
```

La comilla simple cierra el texto utilizado por el `LIKE`, mientras que `OR 1=1` incorpora una condicion que siempre es verdadera. Finalmente, `--` comenta el resto de la consulta original.

Como `1=1` siempre es verdadero, la aplicacion devuelve todas las funciones disponibles, aunque el texto ingresado no corresponda al nombre de una pelicula.

![Resultado de la inyeccion mediante OR 1=1](Ejercicio1/Images/1.png)

### POC 2 - Consulta de informacion mediante `UNION SELECT`

Para realizar esta prueba se utilizo primero un nombre de pelicula inexistente. De esta forma, la consulta original no devuelve resultados y en la interfaz se muestra que no se encontraron peliculas.

Luego se agrego una consulta mediante `UNION SELECT` para obtener informacion adicional de la base de datos.

**Entrada utilizada:**

```text
NoHayPeliculas' UNION SELECT name, '2026-09-01', 0 FROM sqlite_master WHERE type='table' --
```

La consulta inyectada debe devolver tres columnas, ya que el `SELECT` original tambien devuelve tres:

1. Nombre de la pelicula.
2. Fecha y hora.
3. Cantidad de asientos disponibles.

La utilizacion de `UNION SELECT` permite combinar el resultado original con informacion proveniente de otra tabla. En SQLite puede consultarse `sqlite_master` para obtener los nombres o las definiciones de las tablas existentes.

**Informacion obtenida:**

![Resultado de la consulta mediante UNION SELECT](Ejercicio1/Images/2.png)

### POC 3 - Modificacion del ordenamiento mediante la URL

Como base para esta prueba, se realizo una busqueda normal utilizando la letra:

```text
s
```

La aplicacion devolvio las peliculas cuyos nombres contienen la letra indicada. Esto permite registrar el comportamiento legitimo antes de implementar la mitigacion y compararlo posteriormente.

![Busqueda normal utilizando la letra s](Ejercicio1/Images/3.png)


Luego se trato de modificar la URL de la aplicacion mediante el parametro `sentido` de la URL.

Una solicitud normal utiliza una URL similar a:

```text
http://localhost:5000/?buscar=s&ordenar_por=nombre&sentido=ASC
```

En la version vulnerable, el valor de `sentido` se agregaba directamente al final de la consulta SQL. Por este motivo, se modifico manualmente la URL para incorporar un `LIMIT`:

```text
http://localhost:5000/?buscar=s&ordenar_por=nombre&sentido=ASC%20LIMIT%201
```

El codigo `%20` representa un espacio dentro de la URL. Flask interpreta el valor recibido como:

```text
ASC LIMIT 1
```

La consulta resultante termina con:

```sql
ORDER BY peliculas.nombre ASC LIMIT 1;
```

Como resultado, la aplicacion muestra unicamente un registro, aunque la busqueda normal con la letra `s` devolvia varios resultados.

Esta prueba demuestra que una SQL injection no tiene que provenir de un campo de texto. Tambien puede introducirse modificando los parametros de una URL.

![Modificacion del parametro sentido mediante la URL](Ejercicio1/Images/4.png)


## Mitigacion

Para mitigar la vulnerabilidad se modifico la funcion `buscar_funciones()` aplicando dos medidas:

1. Parametrizacion del termino de busqueda.
2. Validacion de los valores utilizados para ordenar los resultados.

El codigo corregido quedo de la siguiente manera:

```python
def buscar_funciones(query, sort_by, sort_dir='ASC'):

    if sort_by == 'fecha':
        sort_by = 'funciones.fecha_hora'
    else:
        sort_by = 'peliculas.nombre'

    sort_dir=sort_dir.upper()
    if sort_dir not in ('ASC', 'DESC'):
        sort_dir = 'ASC'

    db = get_db()
    sql = f"SELECT peliculas.nombre as pelicula, funciones.fecha_hora, " \
          f"(funciones.asientos_totales - funciones.asientos_ocupados) as disponibles " \
          f"FROM funciones " \
          f"JOIN peliculas ON funciones.pelicula_id = peliculas.id " \
          f"WHERE peliculas.nombre LIKE ? " \
          f"ORDER BY {sort_by} {sort_dir}"
    return db.execute(sql, (f"%{query}%",)).fetchall()
```

### Parametrizacion de la busqueda

En la versiona con la vulnerabilidad el valor ingresado por el usuario se colocaba directamente dentro del SQL:

```python
f"WHERE peliculas.nombre LIKE '%{query}%' "
```

Esto permitia que una entrada con instrucciones SQL modificara la consulta.

Se reemplazo por un parametro:

```python
"WHERE peliculas.nombre LIKE ? "
```

El valor se envia separadamente al ejecutar la consulta:

```python
db.execute(
    sql,
    (f"%{query}%",)
)
```

De esta manera, SQLite interpreta todo el contenido de `query` como un dato y no como parte de la consulta SQL.

Los simbolos `%` se agregan al parametro para mantener la busqueda parcial realizada mediante `LIKE`.

### Validacion de la columna de ordenamiento

Los nombres de columnas no pueden parametrizarse utilizando `?`. Por este motivo, el valor recibido mediante `sort_by` se transforma en una columna definida por la aplicacion:

```python
if sort_by == 'fecha':
    sort_column = 'funciones.fecha_hora'
else:
    sort_column = 'peliculas.nombre'
```

Los unicos valores que pueden llegar al `ORDER BY` son:

```sql
funciones.fecha_hora
```

o

```sql
peliculas.nombre
```

Si se recibe cualquier otro valor, se utiliza `peliculas.nombre` como opcion predeterminada.

### Validacion del sentido de ordenamiento

El parametro `sort_dir` se obtiene desde la URL y, en la version vulnerable, se agregaba directamente al final de la consulta.

Primero se transforma el valor a mayusculas:

```python
sort_dir = sort_dir.upper()
```

Luego se verifica que sea uno de los dos sentidos permitidos:

```python
if sort_dir not in ('ASC', 'DESC'):
    sort_dir = 'ASC'
```

Esto evita que se agreguen nuevas instrucciones mediante el parametro `sentido` de la URL.

## Verificacion de la mitigacion

Despues de modificar el codigo, se repitieron las pruebas realizadas sobre la version vulnerable. El objetivo fue comprobar que la SQL injection ya no pudiera reproducirse y que las busquedas legitimas continuaran funcionando.

### Comprobacion 1 - Bloqueo de la inyeccion en el buscador

Se volvio a ingresar el valor utilizado anteriormente para modificar la condicion de la consulta:

```sql
' OR 1=1 --
```

En la version vulnerable, esta entrada provocaba que la condicion fuera siempre verdadera y mostraba todas las funciones.

Despues de la mitigacion, el valor es enviado separadamente mediante el parametro `?`:

```python
"WHERE peliculas.nombre LIKE ?"
```

```python
db.execute(sql, (f"%{query}%",))
```

SQLite interpreta la entrada completa como un texto que debe buscarse en el nombre de una pelicula. Por lo tanto, `OR 1=1` y `--` dejan de interpretarse como instrucciones SQL.

Como no existe una pelicula con ese contenido en su nombre, la aplicacion no devuelve resultados.

![Inyeccion del buscador bloqueada despues de la mitigacion](Ejercicio1/Images/5.png)
![Inyeccion del buscador bloqueada despues de la mitigacion](Ejercicio1/Images/6.png)

### Comprobacion 2 - Bloqueo de la modificacion mediante la URL

Finalmente, se volvio a modificar el parametro `sentido` para intentar agregar un `LIMIT 1`:

```text
http://localhost:5000/?buscar=s&ordenar_por=nombre&sentido=ASC%20LIMIT%201
```

El servidor recibe el siguiente valor:

```text
ASC LIMIT 1
```

Sin embargo, este valor no se encuentra dentro de los sentidos permitidos:

```python
if sort_dir not in ('ASC', 'DESC'):
    sort_dir = 'ASC'
```

Por este motivo, la aplicacion reemplaza el contenido recibido por:

```text
ASC
```

La consulta se ejecuta sin el `LIMIT 1` agregado desde la URL y muestra nuevamente todos los resultados correspondientes a la busqueda.

![Modificacion mediante URL bloqueada despues de la mitigacion](Ejercicio1/Images/7.png)

---

# Ejercicio 2 - Cross-Site Scripting (XSS)

## Marco teorico

Una vulnerabilidad Cross-Site Scripting, tambien conocida como XSS, ocurre cuando una aplicacion muestra un dato ingresado por el usuario y el navegador lo interpreta como HTML o JavaScript.

Esto puede permitir que una persona introduzca codigo que se ejecutara cuando otro usuario visite la pagina vulnerable.

Las entradas utilizadas en un XSS pueden provenir de:
- Campos de texto.
- Formularios.
- Parametros de la URL.
- Datos almacenados en una base de datos.
- Cuerpos JSON.
- Cookies.

Existen diferentes tipos de XSS:

- **XSS reflejado:** el contenido llega en una solicitud y se muestra inmediatamente.
- **XSS almacenado:** el contenido se guarda y se ejecuta posteriormente cuando se vuelve a mostrar.
- **XSS basado en DOM:** el JavaScript del frontend introduce el contenido inseguro dentro de la pagina.


## Identificacion de la vulnerabilidad

En este ejercicio se presenta un XSS almacenado, ya que el contenido ingresado se guarda en la base de datos y se ejecuta posteriormente al volver a abrir la edicion de la pelicula.

La aplicacion permite modificar los datos de una pelicula mediante un formulario de edicion.

Cuando se guarda el formulario, Flask obtiene los siguientes valores:

```python
nombre = request.form.get('nombre', '')
genero = request.form.get('genero', '')
director = request.form.get('director', '')
descripcion = request.form.get('descripcion', '')
```

Luego, los datos se almacenan en la base de datos:

```python
db.execute(
    '''UPDATE peliculas
       SET nombre=?, genero=?, director=?, descripcion=?
       WHERE id=?''',
    (nombre, genero, director, descripcion, pelicula_id),
)
```

La consulta se encuentra parametrizada, por lo que el contenido se guarda como un dato. Sin embargo, esta parametrizacion solamente protege contra SQL injection y no evita que el contenido pueda producir un XSS cuando posteriormente se muestra en el navegador.

Al volver a abrir la edicion de la pelicula, la descripcion guardada se muestra de la siguiente manera:

```html
{{ pelicula['descripcion'] | safe }}
```

El filtro:

```text
safe
```

le indica al motor de plantillas que el contenido es confiable y que puede mostrarse como HTML sin escapar sus caracteres.

Por este motivo, si la descripcion contiene etiquetas HTML o JavaScript, el navegador puede interpretarlas y ejecutarlas.

## Prueba de concepto (PoC)

Para comprobar la vulnerabilidad se modifico la descripcion de una pelicula desde la pagina de edicion.

### POC 1 - Ingreso del codigo en la descripcion

Primero se ingreso el siguiente contenido en el campo `Descripcion`:

```html
<script>alert('XSS')</script>
```

Luego se presiono el boton `Guardar cambios`.

El contenido fue recibido por Flask y almacenado en la columna `descripcion` de la tabla `peliculas`.

![Ingreso del codigo XSS en la descripcion](Ejercicio2/Images/1.png)

Despues de guardar los cambios, se volvio a abrir la pagina de edicion de la misma pelicula.

Como consecuencia de lo realizado anteriormente, el navegador interpreto la etiqueta `script` y ejecuto:

```javascript
alert('XSS')
```

La aparicion de la alerta demuestra que fue posible ejecutar JavaScript introducido por el usuario.

![Ejecucion del codigo XSS almacenado](Ejercicio2/Images/2.png)

La entrada continua almacenada en la base de datos despues de guardar los cambios.

Por este motivo, cada vez que se vuelve a abrir la edicion de la pelicula, el navegador vuelve a procesar el contenido guardado.

Esto permite clasificar la vulnerabilidad como un XSS almacenado.

![Persistencia del contenido XSS](Ejercicio2/Images/3.png)


## Mitigacion

Para mitigar la vulnerabilidad se elimino el filtro `safe` utilizado al mostrar la descripcion.

El codigo vulnerable era:

```html
{{ pelicula['descripcion'] | safe }}
```

Se reemplazo por:

```html
{{ pelicula['descripcion'] }}
```

La seccion corregida de `edit.html` quedo de la siguiente manera:

```html
{% if pelicula['descripcion'] %}
    <div class="prev-descripcion">
        <strong>Descripcion actual:</strong><br>
            {{ pelicula['descripcion'] | safe }}
    </div>
{% endif %}
```

## Verificacion de la mitigacion

Despues de eliminar el filtro `safe`, se repitieron las pruebas realizadas.

### Comprobacion 1 - Bloqueo de la ejecucion de JavaScript

Se volvio a guardar el siguiente contenido en la descripcion:

```html
<script>alert('XSS')</script>
```

Despues se abrio nuevamente la edicion de la pelicula.

![Codigo JavaScript bloqueado despues de la mitigacion](Ejercicio2/Images/3.png)

El contenido ingresado se mostro literalmente en la pagina:

```text
<script>alert('XSS')</script>
```

El navegador dejo de interpretarlo como codigo HTML o JavaScript.