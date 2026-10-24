import pytest
import requests

BASE_URL = "http://localhost:8080"

@pytest.fixture
def client():
    """
    Crea un cliente HTTP para enviar solicitudes a la
    aplicacion Spring que se encuentra ejecutando en Docker.
    """
    cliente = requests.Session()

    yield cliente

    cliente.close()


def test_expresion_spel_no_se_ejecuta(client):
    # Enviamos una expresion matematica en el buscador.
    # En la version vulnerable, SpEL calcula 4*2 y obtiene 8.
    respuesta = client.get(
        BASE_URL,
        params={
            "buscar": "4*2"
        },
        timeout=5
    )

    contenido = respuesta.text

    print("\nURL solicitada:")
    print(respuesta.url)

    print("\nCódigo de respuesta:")
    print(respuesta.status_code)

    # La busqueda no debe provocar un error del servidor.
    assert respuesta.status_code == 200

    # La aplicacion no debe mostrar el resultado de evaluar 4*2.
    assert "Resultados buscando por: 8" not in contenido

    # Debe buscar el texto literalmente. Como no existe una funcion con ese nombre, no debe encontrar coincidencias.
    assert "No se encontraron coincidencias" in contenido


def test_busqueda_normal_funciona(client):
    # Comprobamos que una busqueda habitual siga funcionando despues de quitar la evaluacion de SpEL.
    respuesta = client.get(
        BASE_URL,
        params={
            "buscar": "aveng"
        },
        timeout=5
    )

    contenido = respuesta.text

    print("\nURL solicitada:")
    print(respuesta.url)

    print("\nCódigo de respuesta:")
    print(respuesta.status_code)

    # La aplicacion debe responder sin error.
    assert respuesta.status_code == 200

    # La busqueda debe encontrar la funcion Avengers.
    assert "Avengers" in contenido