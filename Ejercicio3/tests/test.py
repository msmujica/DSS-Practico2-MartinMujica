import uuid

import pytest
import requests

BASE_URL = "http://localhost:8080"
PELICULA_ID = 1


@pytest.fixture
def client():
    """
    Crea un cliente HTTP para enviar solicitudes a la
    aplicacion Java que se encuentra ejecutando en Docker.
    """
    cliente = requests.Session()

    yield cliente

    cliente.close()


def test_rechaza_archivo_txt(client):
    # El UUID evita que el nombre coincida con un archivo que haya quedado de una ejecucion anterior.
    nombre_archivo = f"prueba_{uuid.uuid4()}.txt"

    # Intentamos subir un archivo de texto como si fuera un afiche.
    respuesta = client.post(
        f"{BASE_URL}/upload/{PELICULA_ID}",
        files={
            "afiche": (
                nombre_archivo,
                b"Este archivo no es una imagen",
                "text/plain"
            )
        },
        allow_redirects=False,
        timeout=5
    )

    print("\nArchivo enviado:")
    print(nombre_archivo)

    print("\nRedireccion:")
    print(respuesta.headers.get("Location"))

    # El controlador responde mediante una redireccion.
    assert respuesta.status_code in (302, 303)

    # Al rechazar la extension txt, debe volver al formulario de subida de la misma pelicula.
    assert respuesta.headers.get(
        "Location", ""
    ).endswith(f"/upload/{PELICULA_ID}")

    # Intentamos acceder al archivo usando el nombre enviado.
    respuesta_archivo = client.get(
        f"{BASE_URL}/uploads/{nombre_archivo}",
        timeout=5
    )

    # Si fue rechazado, no debe estar disponible.
    assert respuesta_archivo.status_code == 404


def test_acepta_jpg_y_cambia_nombre(client):
    # Generamos un nombre original distinto en cada ejecucion.
    nombre_archivo = f"afiche_{uuid.uuid4()}.jpg"

    # Contenido enviado como archivo con extension jpg.
    contenido_jpg = (
        b"\xff\xd8\xff\xe0"
        b"imagen-de-prueba"
        b"\xff\xd9"
    )

    # Enviamos el archivo al endpoint de subida.
    respuesta = client.post(
        f"{BASE_URL}/upload/{PELICULA_ID}",
        files={
            "afiche": (
                nombre_archivo,
                contenido_jpg,
                "image/jpeg"
            )
        },
        allow_redirects=False,
        timeout=5
    )

    print("\nArchivo enviado:")
    print(nombre_archivo)

    print("\nRedireccion:")
    print(respuesta.headers.get("Location"))

    # La solicitud termina con una redireccion.
    assert respuesta.status_code in (302, 303)

    # Para una extension permitida, el controlador redirige a la pagina principal.
    assert respuesta.headers.get(
        "Location", ""
    ).endswith("/")

    # Intentamos acceder al archivo usando el nombre original.
    respuesta_nombre_original = client.get(
        f"{BASE_URL}/uploads/{nombre_archivo}",
        timeout=5
    )

    # Debe devolver 404 porque la aplicacion reemplaza el nombre original por uno generado con UUID.
    assert respuesta_nombre_original.status_code == 404