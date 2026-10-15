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
    Crea un cliente de prueba conectado directamente
    con la aplicación Flask.
    """
    app.config.update(
        TESTING=True
    )

    with app.test_client() as cliente:
        yield cliente


def contar_resultados(contenido):
    """
    Una película puede aparecer más de una vez porque puede
    tener varias funciones.
    """
    return sum(
        contenido.count(pelicula)
        for pelicula in PELICULAS
    )


def test_busqueda_normal(client):
    respuesta = client.get(
        "/",
        query_string={
            "buscar": "Dune: Parte Dos",
            "ordenar_por": "nombre",
            "sentido": "ASC"
        }
    )

    contenido = respuesta.get_data(as_text=True)
    cantidad = contar_resultados(contenido)

    print(f"\nCantidad de resultados: {cantidad}")

    assert respuesta.status_code == 200

    assert "Dune: Parte Dos" in contenido
    assert "Godzilla x Kong: El Nuevo Imperio" not in contenido
    assert "La Sociedad de la Nieve" not in contenido

    assert cantidad == 3


def test_busqueda_injection_or(client):
    respuesta = client.get(
        "/",
        query_string={
            "buscar": "' OR 1=1 --",
            "ordenar_por": "nombre",
            "sentido": "ASC"
        }
    )

    contenido = respuesta.get_data(as_text=True)
    cantidad = contar_resultados(contenido)

    print(f"\nCantidad devuelta por OR 1=1: {cantidad}")

    assert respuesta.status_code == 200

    assert cantidad == 0

    assert "Dune: Parte Dos" not in contenido
    assert "Godzilla x Kong: El Nuevo Imperio" not in contenido
    assert "La Sociedad de la Nieve" not in contenido


def test_busqueda_injection_url(client):
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

    # La búsqueda por "s" devuelve nueve funciones.
    # El LIMIT 1 no debe modificar la consulta.
    assert cantidad == 9

    assert "La Sociedad de la Nieve" in contenido
    assert "Spider-Man: Across the Spider-Verse" in contenido
    assert "Poor Things" in contenido
    assert "Transformers One" in contenido