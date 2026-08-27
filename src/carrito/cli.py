"""Línea de comandos del carrito."""

import argparse

from carrito.datos import pedido
from carrito.descuentos import PROMOCIONES
from carrito.precios import precio_linea
from carrito.resumen import resumen


def formatear_monto(monto: int) -> str:
    """Formatea un monto en pesos con punto como separador de miles."""
    return f"{monto:,}".replace(",", ".")


def main():
    parser = argparse.ArgumentParser(prog="carrito")
    parser.add_argument("comando", choices=["total"])
    parser.add_argument("--pedido", type=int, required=True)
    parser.add_argument("--sin", action="append", choices=sorted(PROMOCIONES), default=[])
    parser.add_argument("--detalle", action="store_true")
    args = parser.parse_args()

    elegido = pedido(args.pedido)
    elegido.promociones = [p for p in elegido.promociones if p not in args.sin]

    filas = []
    if args.detalle:
        filas += [
            (f"{linea.producto.nombre} x {linea.cantidad}", formatear_monto(precio_linea(linea)))
            for linea in elegido.lineas
        ]
    num_detalle = len(filas)

    filas += [(etiqueta, formatear_monto(monto)) for etiqueta, monto in resumen(elegido).items()]

    ancho_etiqueta = max(len(etiqueta) for etiqueta, _ in filas)
    ancho_monto = max(len(monto) for _, monto in filas)
    for i, (etiqueta, monto) in enumerate(filas):
        print(f"{etiqueta:<{ancho_etiqueta}}  {monto:>{ancho_monto}}")
        if num_detalle and i == num_detalle - 1:
            print("-")


if __name__ == "__main__":
    main()
