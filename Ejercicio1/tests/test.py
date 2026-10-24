import pytest
from app import app

PELICULAS = [
    "Dune: Parte Dos",
    "Oppenheimer",
    "Spider-Man: Across the Spider-Verse",
    "La Sociedad de la Nieve",
    "Poor Things",
    "Wonka",
    "Kung Fu Panda 4",
    "Godzilla x Kong: El Nuevo Imperio",
    "Pobres Criaturas",
    "Transformers One",
]


@pytest.fixture
def client():
    """
    Prepara un cliente de pruebas de Flask.

    Permite hacer solicitudes a la aplicacion sin abrir el navegador
    ni iniciar el servidor con python app.py.
    """
    app.config.update(TESTING=True)

    with app.test_client() as cliente:
        yield cliente


def contar_resultados(contenido):
    """
    Cuenta las apariciones de peliculas en el HTML recibido.

    Una misma pelicula puede aparecer varias veces porque tiene
    varias funciones. Por eso contamos apariciones y no peliculas
    diferentes.
    """
    return sum(
        contenido.count(pelicula)
        for pelicula in PELICULAS
    )


def test_busqueda_injection_or(client):
    # Enviamos por el buscador el mismo payload utilizado para explotar la SQL Injection.
    respuesta = client.get(
        "/",
        query_string={
            "buscar": "' OR 1=1 --",
            "ordenar_por": "nombre",
            "sentido": "ASC"
        }
    )

    # Obtenemos el HTML que genero la aplicacion.
    contenido = respuesta.get_data(as_text=True)
    cantidad = contar_resultados(contenido)

    print(f"\nCantidad devuelta por OR 1=1: {cantidad}")

    # La solicitud debe procesarse sin generar un error HTTP.
    assert respuesta.status_code == 200

    # Como no existe una pelicula con ese nombre, no hay resultados.
    assert cantidad == 0

    # Confirmamos tambien que no se filtraron peliculas concretas.
    assert "Dune: Parte Dos" not in contenido
    assert "Godzilla x Kong: El Nuevo Imperio" not in contenido
    assert "La Sociedad de la Nieve" not in contenido


def test_busqueda_injection_url(client):
    # Buscamos peliculas que contengan "s", pero agregemas un LIMIT 1 mediante el parametro de ordenamiento.
    respuesta = client.get(
        "/",
        query_string={
            "buscar": "s",
            "ordenar_por": "nombre",
            "sentido": "ASC LIMIT 1"
        }
    )

    contenido = respuesta.get_data(as_text=True)
    cantidad = contar_resultados(contenido)

    print(f"\nCantidad devuelta usando ASC LIMIT 1: {cantidad}")

    assert respuesta.status_code == 200

    # Con los datos iniciales hay 12 funciones que coinciden con "s".
    # Si se aplicara el LIMIT inyectado, apareceria solamente una.
    assert cantidad == 12

    # Comprobamos que la busqueda legitima sigue mostrando diferentes peliculas despues de rechazar el LIMIT.
    assert "Dune: Parte Dos" in contenido
    assert "La Sociedad de la Nieve" in contenido
    assert "Spider-Man: Across the Spider-Verse" in contenido
    assert "Poor Things" in contenido
    assert "Transformers One" in contenido