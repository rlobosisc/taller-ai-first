"""Verifica la política de orden de descuentos documentada.

README.md ("Cómo se arma el total") y el docstring de carrito.descuentos
dicen que los cupones porcentuales se aplican primero, y sobre el monto que
queda se aplican los vales de monto fijo.
"""

from carrito.descuentos import total_con_descuentos
from carrito.modelo import Cupon, Linea, Pedido, Producto


def test_cupon_porcentual_se_aplica_antes_que_vale_de_monto_fijo():
    producto = Producto(sku="SKU-1", nombre="Producto de prueba", precio=1000)
    pedido = Pedido(
        numero=1,
        lineas=[Linea(producto=producto, cantidad=1)],
        cupones=[
            Cupon(codigo="10PORCIENTO", tipo="porcentaje", valor=10),
            Cupon(codigo="VALE100", tipo="monto", valor=100),
        ],
    )

    # Subtotal: 1000
    # 1) Cupón porcentual (10%): 1000 - 100 = 900
    # 2) Vale de monto fijo ($100): 900 - 100 = 800
    assert total_con_descuentos(pedido) == 800
