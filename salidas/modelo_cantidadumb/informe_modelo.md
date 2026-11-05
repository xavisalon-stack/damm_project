# Informe del modelo predictivo

## Objetivo

Predecir la suma semanal de `CantidadUMB` por `Establecimiento` y `Material` para los próximos 7 días.

El resultado es una **previsión de compra**, no una estimación de consumo real.

## Preparación

- 553,465 filas originales agregadas por establecimiento, material y semana.
- Los valores negativos se conservaron al sumar; no se reinterpretaron sin un indicador documental.
- Las ausencias se convirtieron en cero únicamente desde la primera aparición de cada serie.
- Las variables históricas se desplazan al menos un periodo para evitar fuga futura.
- No se mezclan productos al calcular métricas: WAPE y sesgo se calculan primero por material.
- No se usa una referencia estacional anual: solo existe un año y no puede validarse.

## Validación temporal

- Cortes de validación: 2025-10-06, 2025-11-03, 2025-12-01.
- Prueba final: 2025-12-08, 2025-12-15, 2025-12-22, 2025-12-29.
- No se realizó división aleatoria.

WAPE macro medio de validación por producto:

| Método | WAPE macro |
|---|---:|
| media_movil_4 | 2.9548 |
| modelo_global_directo | 3.3707 |
| ultima_cantidad | 4.6598 |
| modelo_global_dos_etapas | 4.8717 |

Modelo seleccionado: `media_movil_4`.

La selección usa el menor WAPE macro por producto en validación, no la complejidad.

Resultados en prueba final:

| Método | WAPE macro | Frecuentes | Intermitentes |
|---|---:|---:|---:|
| ultima_cantidad | 1.4560 | 1.2178 | 1.7493 |
| media_movil_4 | 1.8203 | 1.2112 | 2.6453 |
| modelo_global_directo | 4.5969 | 1.1177 | 7.2786 |
| modelo_global_dos_etapas | 7.7092 | 8.6051 | 9.3327 |

En prueba, `ultima_cantidad` obtiene el menor WAPE macro. `media_movil_4` logra 1.2112 en series frecuentes y 2.6453 en intermitentes.
La mejora observada en validación no es robusta en la prueba final; no se justifica atribuir una ganancia estable al aprendizaje automático.

## Previsión

- Inicio del horizonte: 2026-01-05.
- El pedido recomendado es orientativo e igual a la previsión: no se dispone de stock, entradas, mínimos ni conversiones comerciales.
- La unidad de UMB no está confirmada y se deja vacía en la salida estructurada.

## Limitaciones

- Solo hay 52 semanas de 2025.
- No se conocen altas, bajas ni descatalogaciones.
- No hay identificador de documento en ventas para clasificar devoluciones o anulaciones.
- El extracto termina mucho antes de la fecha de generación; las propuestas no deben usarse operativamente sin actualizar el histórico.
