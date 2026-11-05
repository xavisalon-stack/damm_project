# Previsión semanal de pedidos

Sistema reproducible para predecir la suma de `CantidadUMB` que comprará cada
`Establecimiento` de cada `Material` durante los próximos 7 días.

La salida es una **previsión de compra**, no consumo real. La propuesta de
pedido es orientativa porque los datos no incluyen stock, entradas confirmadas,
mínimos de pedido ni conversiones comerciales.

## Instalación

```bash
python3 -m pip install -r requirements.txt
```

## Entrenamiento, validación y predicción

```bash
PYTHONPATH=src python3 -m pedido_predictivo.cli entrenar \
  --datos datos/ventas_sample.xlsx \
  --salida salidas/modelo_cantidadumb
```

El proceso:

1. Valida las columnas y agrega sin mezclar productos.
2. Regulariza cada serie desde su primera observación.
3. Crea variables históricas desplazadas.
4. Compara última cantidad, media móvil, modelo global directo y modelo global
   en dos etapas.
5. Selecciona por WAPE macro por producto en validación cronológica.
6. Evalúa en las últimas cuatro semanas y genera el horizonte siguiente.

No se utiliza referencia estacional porque solo hay 52 semanas y no puede
validarse con un año anterior.

## Resultados

La carpeta de salida contiene:

- `comparativa_modelos.csv`
- `metricas_prueba_por_producto.csv`
- `metricas_prueba_por_serie.csv`
- `previsiones_pedidos.csv`
- `modelo.joblib`
- `informe_modelo.md`

Consultar o exportar un establecimiento:

```bash
PYTHONPATH=src python3 -m pedido_predictivo.cli consultar \
  --establecimiento 7000004735 \
  --mensaje

PYTHONPATH=src python3 -m pedido_predictivo.cli consultar \
  --establecimiento 7000004735 \
  --exportar propuesta_establecimiento.csv
```

La consulta no envía mensajes ni genera pedidos.

## Pruebas

```bash
python3 -m pytest
```

Las pruebas cubren fuga temporal, separación de unidades por producto,
devoluciones negativas, predicciones no negativas, series nuevas y redondeos
comerciales.
