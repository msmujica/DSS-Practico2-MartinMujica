import uuid

import pytest
import requests


BASE_URL = "http://localhost:8080"
PELICULA_ID = 1


@pytest.fixture
def client():
    """
    Cliente HTTP conectado con la aplicacion Java ejecutada en Docker.
    """
    cliente = requests.Session()

    yield cliente

    cliente.close()


def test_rechaza_archivo_txt(client):
    nombre_archivo = f"prueba_{uuid.uuid4()}.txt"

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

    assert respuesta.status_code in (302, 303)

    # El archivo no permitido debe ser rechazado.
    assert respuesta.headers.get(
        "Location", ""
    ).endswith(f"/upload/{PELICULA_ID}")

    # No debe quedar almacenado publicamente.
    respuesta_archivo = client.get(
        f"{BASE_URL}/uploads/{nombre_archivo}",
        timeout=5
    )

    assert respuesta_archivo.status_code == 404


def test_acepta_jpg_y_cambia_nombre(client):
    nombre_archivo = f"afiche_{uuid.uuid4()}.jpg"

    contenido_jpg = (
        b"\xff\xd8\xff\xe0"
        b"imagen-de-prueba"
        b"\xff\xd9"
    )

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

    assert respuesta.status_code in (302, 303)

    # El JPG debe ser aceptado y regresar al inicio.
    assert respuesta.headers.get(
        "Location", ""
    ).endswith("/")

    # El archivo no debe guardarse con su nombre original.
    respuesta_nombre_original = client.get(
        f"{BASE_URL}/uploads/{nombre_archivo}",
        timeout=5
    )

    assert respuesta_nombre_original.status_code == 404