import pytest

from app import app


@pytest.fixture
def client():
    """
    Crea un cliente conectado directamente con la aplicacion Flask.
    """
    app.config.update(
        TESTING=True
    )

    with app.test_client() as cliente:
        yield cliente

def test_descripcion_xss(client):
    payload = "<script>alert('XSS')</script>"

    # Guarda el payload en la descripcion de la pelicula.
    respuesta_guardado = client.post(
        "/edit/1",
        data={
            "nombre": "Dune: Parte Dos",
            "genero": "Ciencia Ficcion",
            "director": "Denis Villeneuve",
            "descripcion": payload
        },
        follow_redirects=True
    )

    assert respuesta_guardado.status_code == 200

    # Abre nuevamente la edicion de la pelicula.
    respuesta = client.get("/edit/1")
    contenido = respuesta.get_data(as_text=True)

    print("\nCodigo de respuesta:")
    print(respuesta.status_code)
    
    assert respuesta.status_code == 200

    # El payload no debe aparecer como HTML ejecutable.
    assert "<script>alert('XSS')</script>" not in contenido

    # La descripcion debe aparecer escapada como texto.
    assert "&lt;script&gt;" in contenido
    assert "&lt;/script&gt;" in contenido