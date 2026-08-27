"""Línea de comandos del carrito."""

import argparse

from carrito.datos import pedido
from carrito.descuentos import PROMOCIONES
from carrito.precios import precio_linea
from carrito.resumen import resumen


def main():
    parser = argparse.ArgumentParser(prog="carrito")
    parser.add_argument("comando", choices=["total"])
    parser.add_argument("--pedido", type=int, required=True)
    parser.add_argument("--sin", action="append", choices=sorted(PROMOCIONES), default=[])
    parser.add_argument("--detalle", action="store_true")
    args = parser.parse_args()

    elegido = pedido(args.pedido)
    elegido.promociones = [p for p in elegido.promociones if p not in args.sin]
    if args.detalle:
        for linea in elegido.lineas:
            print(linea.producto.nombre, "x", linea.cantidad, precio_linea(linea))
        print("-")
    datos = resumen(elegido).items()
    ancho_etiqueta = max(len(etiqueta) for etiqueta, _ in datos)
    ancho_monto = max(len(str(monto)) for _, monto in datos)
    for etiqueta, monto in datos:
        print(f"{etiqueta:<{ancho_etiqueta}}  {monto:>{ancho_monto}}")


if __name__ == "__main__":
    main()
