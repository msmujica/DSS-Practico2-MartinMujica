import pytest
from app import app


@pytest.fixture
def client():
    """
    Prepara un cliente de pruebas de Flask.

    Permite enviar solicitudes a los endpoints sin abrir
    un navegador ni iniciar el servidor manualmente.
    """
    app.config.update(TESTING=True)

    with app.test_client() as cliente:
        yield cliente


def test_descripcion_xss(client):
    # Este contenido se utilizo en la prueba de concepto.
    # Si el navegador lo interpreta como HTML, ejecuta el script.
    payload = "<script>alert('XSS')</script>"

    # Enviamos el formulario de edicion de la pelicula.
    # La aplicacion guarda el payload en el campo descripcion.
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

    # Comprobamos que la solicitud de guardado termino correctamente.
    assert respuesta_guardado.status_code == 200

    # Abrimos nuevamente la edicion para comprobar como se muestra la descripcion almacenada.
    respuesta = client.get("/edit/1")
    html = respuesta.get_data(as_text=True)

    assert respuesta.status_code == 200

    # Este bloque debe aparecer porque la pelicula tiene una descripcion guardada.
    assert "Descripción actual:" in html

    # Extraemos solo el bloque donde estaba el filtro vulnerable |safe.
    descripcion_actual = html.split(
        '<div class="prev-descripcion">', 1
    )[1].split("</div>", 1)[0]

    print("\nDescripcion actual generada en el HTML:")
    print(descripcion_actual)

    # El contenido no se elimina. El texto del ataque sigue presente.
    assert "alert(" in descripcion_actual

    # Las etiquetas deben estar escapadas para que el navegador las muestre como texto en lugar de ejecutarlas.
    assert "&lt;script&gt;" in descripcion_actual
    assert "&lt;/script&gt;" in descripcion_actual

    assert "<script>" not in descripcion_actual
    assert "</script>" not in descripcion_actual