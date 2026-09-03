# CLAUDE.md

Este archivo guía a Claude Code (claude.ai/code) al trabajar con el código de este repositorio.

## Qué es esto

`carrito`: calcula el total de un pedido — precio de las líneas, descuentos,
cupones, IVA y envío. Es un CLI pequeño respaldado por un dataset JSON fijo
(`datos/ejemplo.json`); no hay base de datos ni capa web.

## Comandos

```sh
uv sync                                    # instala dependencias (Python 3.12+, gestionado con uv)
uv run python -m carrito total --pedido 42 # corre el CLI
uv run pytest                              # corre toda la suite de tests
uv run pytest tests/test_orden_descuentos.py::test_cupon_porcentual_se_aplica_antes_que_vale_de_monto_fijo  # un test puntual
```

Flags del comando `total`: `--pedido N` (obligatorio), `--detalle` (muestra el
precio de cada línea), `--sin PROMO` (repetible; excluye una promoción por
nombre, ej. `--sin 2x1`).

El CI (`.github/workflows/tests.yml`) solo corre `uv sync --locked --all-groups`
y luego `uv run pytest` — no hay un paso de lint separado en este repo.

## Arquitectura

Un pipeline a través de `src/carrito/`, donde cada módulo es dueño de una
etapa del cálculo del total:

1. **`modelo.py`** — solo dataclasses: `Producto`, `Linea`, `Cupon`, `Pedido`.
   No hay lógica acá.
2. **`datos.py`** — carga `datos/ejemplo.json` en objetos `Pedido`/`Producto`.
   `pedido(numero)` es el lookup que usa el resto del código; relee y
   reparsea el archivo JSON en cada llamada (sin cache).
3. **`precios.py`** — `precio_linea` y `subtotal` (suma de las líneas, antes
   de descuentos).
4. **`descuentos.py`** — dos mecanismos de descuento independientes que se
   aplican en un orden específico y no obvio dentro de `total_con_descuentos`:
   - Las **promociones** (diccionario `PROMOCIONES` — `2x1`, `volumen`,
     `primera-compra`) se aplican primero, sobre el subtotal. Cuáles aplican
     viene de `pedido.promociones` (definido en el fixture JSON, filtrable
     desde el CLI con `--sin`).
   - Los **cupones** se aplican después, sobre el monto ya con promociones:
     los porcentuales (`tipo="porcentaje"`) antes que los de monto fijo
     (`tipo="monto"`). Este orden es política de negocio deliberada (ver el
     docstring del módulo y `tests/test_orden_descuentos.py`) — no lo
     reordenes sin revisar ese test.
5. **`dinero.py`** — la convención de redondeo de toda la app:
   `redondear()` redondea al peso más cercano, el medio peso hacia arriba.
   `porcentaje()` (usado por los descuentos) pasa por acá. **`iva()` en
   `impuestos.py` no**: trunca con `int()` en vez de usar `porcentaje()`.
   Es una inconsistencia existente, no un error para "corregir" en
   silencio — confirma con el usuario antes de cambiar el redondeo del IVA.
6. **`envio.py`** — costo de envío por región (`TRAMOS`), gratis sobre
   `UMBRAL_ENVIO_GRATIS` ($50.000). Los clientes nuevos
   (`pedido.cliente_nuevo`) tienen envío gratis sin importar el monto —
   se chequea antes que el umbral.
7. **`resumen.py`** — arma el diccionario final ordenado (Subtotal →
   Descuentos → IVA → Envío → Total) que imprime el CLI. Solo incluye la
   línea "Descuentos" si el monto descontado difiere del subtotal. Nota:
   `ETIQUETAS` en este archivo es código muerto actualmente — el resumen usa
   strings literales en su lugar.
8. **`cli.py`** — punto de entrada con argparse (`comando` por ahora solo
   acepta `"total"`). Lee un pedido, aplica el filtro `--sin`, formatea los
   montos con `.` como separador de miles (`formatear_monto`).

## Detalles a tener en cuenta

- `datos/ejemplo.json` es la única fuente de datos; los pedidos 41–46 son los
  fixtures fijos que se usan para probar el CLI a mano.
- Solo existe un test automatizado (`tests/test_orden_descuentos.py`), que
  cubre específicamente la política de orden de los cupones — no es una
  suite de regresión general para precios, envío o impuestos.
