# Informe EDA: sell_out_ventas_Nielsen_sample.xlsx

Fuente (solo lectura): `datos/sell_out_ventas_Nielsen_sample.xlsx`. Generado: 2026-10-29 16:45 (Europe/Madrid).

El Excel original no se ha modificado. El CSV es una copia con nombres y textos recortados, textos vacíos a nulo y el marcador `#` a nulo.

## 1. Vista general

Hojas (2): `datos` (15000×26), `info` (0×1).

### Hoja `info`

Hoja de documentación: entra en la vista general y no en el resto del EDA.

- Filas: 0. Columnas: 1.

La hoja no tiene filas.

### Hoja `datos`

- Filas: 15000. Columnas: 26. Numéricas: 18. Categóricas: 6. Fechas: 2.

Primeras filas:

Columnas 1 de 4 (marca … segmento).

| # | marca | end_week | markets | sociedades | envase | capacidad | unidades | segmento |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | RESERVA 1925 | 2024-09-29 00:00:00 | CARREFOUR HIPER/ES | S.ALH | BOT | 225 | 06 | Premium |
| 2 | C.CAMPO | 2024-09-29 00:00:00 | CARREFOUR HIPER/ES | S.CC. | LATA | 330 | 01 | Mainstream |
| 3 | CRUZ.DEL.SUR | 2024-09-29 00:00:00 | CARREFOUR HIPER/ES | S.CC. | LATA | 330 | 01 | Discount maisntream |
| 4 | BOCK.DAMM | 2024-09-29 00:00:00 | CARREFOUR HIPER/ES | S.DAMM | BOT | 250 | 06 | Premium |
| 5 | CARLSBERG | 2024-09-29 00:00:00 | CARREFOUR HIPER/ES | S.DAMM | LATA | 330 | 12 | Premium |

Columnas 2 de 4 (vtas_ltrs … vtas_valor).

| # | vtas_ltrs | vtas_ltrs_baseline | vtas_ltrs_cualquier_promo | vtas_ltrs_sin_promo | precio_ltrs_promedio | precio_ltrs_cualquier_promo | precio_ltrs_sin_promo | vtas_valor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3187.35 | 2956.155 | 1742.85 | 1444.5 | 3.796 | 3.794 | 3.8 | 12100.4 |
| 2 | 2018.28 | 1921.354 | 692.67 | 1325.61 | 2.18 | 2.136 | 2.203 | 4399.28 |
| 3 | 3198.69 | 3198.69 | 0.0 | 3198.69 | 1.305 |  | 1.305 | 4173.1 |
| 4 | 76.5 | 75.803 | 1.5 | 75.0 | 3.59 | 3.24 | 3.597 | 274.61 |
| 5 | 601.92 | 612.546 | 31.68 | 570.24 | 2.364 | 2.412 | 2.361 | 1422.99 |

Columnas 3 de 4 (month … intensidad_promocional_porcen).

| # | month | precio_ltrs_promedio_damm | precio_ltrs_cualquier_promo_damm | precio_ltrs_sin_promo_damm | porcen_descuento | porcen_descuento_competencia | uplift_ltrs | intensidad_promocional_porcen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2024-09-30 00:00:00 | 3.796 | 3.794 | 3.8 | 0.158 | 0.0 | 231.195 | 54.68 |
| 2 | 2024-09-30 00:00:00 | 2.18 | 2.136 | 2.203 | 3.041 | 21.956 | 96.926 | 34.32 |
| 3 | 2024-09-30 00:00:00 | 1.305 | 1.305 | 1.305 | 0.0 | 0.0 | 0.0 | 0.0 |
| 4 | 2024-09-30 00:00:00 | 3.59 | 3.24 | 3.597 | 9.925 | 8.267 | 0.697 | 1.961 |
| 5 | 2024-09-30 00:00:00 | 2.364 | 2.412 | 2.361 | 0.0 | 3.912 | -10.626 | 5.263 |

Columnas 4 de 4 (cuota_ltrs_total_mercado_end_week … cuota_valor_total_mercado_end_week).

| # | cuota_ltrs_total_mercado_end_week | cuota_valor_total_mercado_end_week |
| --- | --- | --- |
| 1 | 0.104976 | 0.233455 |
| 2 | 0.066472 | 0.084876 |
| 3 | 0.105349 | 0.080512 |
| 4 | 0.00252 | 0.005298 |
| 5 | 0.019824 | 0.027454 |

## 2. Tipos de variables

Las columnas numéricas incluyen códigos si el Excel los guardó como número. La nota de baja cardinalidad señala las que tienen 15 valores distintos o menos.

### Hoja `datos`


Numéricas:

| Variable | No nulos | Media | Desv. típica | Mín. | P25 | Mediana | P75 | Máx. | Nota |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| capacidad | 15000 | 359 | 209.1 | 200 | 330 | 330 | 330 | 5000 |  |
| vtas_ltrs | 15000 | 3301 | 1.986e+04 | 0.2 | 33.99 | 232.7 | 1207 | 9.595e+05 |  |
| vtas_ltrs_baseline | 15000 | 2175 | 1.318e+04 | 0 | 30.69 | 212 | 1032 | 4.379e+05 |  |
| vtas_ltrs_cualquier_promo | 15000 | 1704 | 1.431e+04 | 0 | 0 | 10.23 | 186 | 9.528e+05 |  |
| vtas_ltrs_sin_promo | 15000 | 1597 | 1.142e+04 | 0 | 21.12 | 137.3 | 668.9 | 4.046e+05 |  |
| precio_ltrs_promedio | 15000 | 3.044 | 1.434 | 0 | 2.186 | 2.635 | 3.535 | 16.67 |  |
| precio_ltrs_cualquier_promo | 10016 | 2.674 | 1.274 | 0 | 1.955 | 2.39 | 3.049 | 28.45 |  |
| precio_ltrs_sin_promo | 14451 | 3.106 | 1.402 | 0.04 | 2.271 | 2.675 | 3.593 | 12.77 |  |
| vtas_valor | 15000 | 6038 | 2.772e+04 | 0 | 105.9 | 675.6 | 3048 | 1.168e+06 |  |
| precio_ltrs_promedio_damm | 15000 | 3.044 | 1.434 | 0 | 2.186 | 2.635 | 3.535 | 16.67 |  |
| precio_ltrs_cualquier_promo_damm | 15000 | 2.907 | 1.424 | 0 | 2.074 | 2.533 | 3.344 | 28.45 |  |
| precio_ltrs_sin_promo_damm | 15000 | 3.107 | 1.438 | 0 | 2.261 | 2.674 | 3.6 | 16.67 |  |
| porcen_descuento | 15000 | 6.831 | 10.66 | 0 | 0 | 0.9065 | 10.15 | 100 |  |
| porcen_descuento_competencia | 15000 | 5.294 | 8.561 | 0 | 0 | 0 | 8.177 | 75.7 |  |
| uplift_ltrs | 15000 | 1126 | 1.299e+04 | -7.771e+04 | 0 | 0.99 | 39.51 | 9.347e+05 |  |
| intensidad_promocional_porcen | 15000 | 22.68 | 32.6 | 0 | 0 | 4.602 | 34.12 | 100 |  |
| cuota_ltrs_total_mercado_end_week | 15000 | 0.3152 | 1.342 | 6e-06 | 0.005998 | 0.03347 | 0.155 | 34.31 |  |
| cuota_valor_total_mercado_end_week | 15000 | 0.3154 | 1.046 | 0 | 0.01013 | 0.04966 | 0.204 | 32.66 |  |

Categóricas:

| Variable | No nulos | Clases | Clase más frecuente | Frecuencia | Nulos | Nota |
| --- | --- | --- | --- | --- | --- | --- |
| marca | 15000 | 265 | EST.GALICIA | 469 | 0.0 % |  |
| markets | 15000 | 11 | CARREFOUR HIPER/ES | 4076 | 0.0 % |  |
| sociedades | 15000 | 14 | S.DAMM | 3282 | 0.0 % |  |
| envase | 15000 | 4 | BOT | 8092 | 0.0 % |  |
| unidades | 15000 | 16 | 01 | 9241 | 0.0 % |  |
| segmento | 15000 | 6 | Premium | 5511 | 0.0 % |  |

Fechas:

| Variable | No nulos | Mínimo | Máximo | Valores distintos |
| --- | --- | --- | --- | --- |
| end_week | 15000 | 2024-01-07 | 2024-12-29 | 32 |
| month | 15000 | 2024-01-31 | 2024-12-31 | 12 |

## 3. Limpieza

No se elimina ninguna columna sin confirmación del usuario. La copia CSV conserva todas las columnas salvo las pasadas con `--excluir-columnas`.

### Hoja `datos`


- Filas duplicadas exactas que permanecen: 0 de 15000 (0.0 %).
- Columnas con nulos:

| Variable | Nulos | % |
| --- | --- | --- |
| precio_ltrs_cualquier_promo | 4984 | 33.2 % |
| precio_ltrs_sin_promo | 549 | 3.7 % |

Columnas poco útiles. Propuesta, no eliminadas de esta ejecución salvo que figuren más abajo como confirmadas:

| Variable | Motivo |
| --- | --- |
| precio_ltrs_promedio_damm | copia exacta de precio_ltrs_promedio |

- Datos de esta hoja: [datos_limpios.csv](datos_limpios.csv).

## 4. Valores atípicos

Criterio del rango intercuartílico sobre cada variable numérica de medida.

### Hoja `datos`


Un valor es atípico si está por debajo de Q1 − 1,5·IQR o por encima de Q3 + 1,5·IQR. Las líneas discontinuas del boxplot marcan esas vallas.

Nota de `vtas_ltrs`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `vtas_ltrs_baseline`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `vtas_ltrs_cualquier_promo`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `vtas_ltrs_sin_promo`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `precio_ltrs_promedio`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `precio_ltrs_cualquier_promo`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `precio_ltrs_sin_promo`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `vtas_valor`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `precio_ltrs_promedio_damm`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `precio_ltrs_cualquier_promo_damm`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `precio_ltrs_sin_promo_damm`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `porcen_descuento`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `porcen_descuento_competencia`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `uplift_ltrs`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `intensidad_promocional_porcen`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `cuota_ltrs_total_mercado_end_week`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

Nota de `cuota_valor_total_mercado_end_week`: Puntos atípicos omitidos en el gráfico por volumen; el recuento está en la tabla.

| Variable | Q1 | Q3 | IQR | Vallas | Atípicos | Boxplot |
| --- | --- | --- | --- | --- | --- | --- |
| capacidad | 330 | 330 | 0 | — | — | criterio no aplicable (IQR nulo) |
| vtas_ltrs | 33.99 | 1207 | 1173 | -1726 … 2967 | 2106 (14.0 %) | ![Boxplot de vtas_ltrs](graficos/datos_box_vtas_ltrs.png) |
| vtas_ltrs_baseline | 30.69 | 1032 | 1001 | -1471 … 2533 | 2041 (13.6 %) | ![Boxplot de vtas_ltrs_baseline](graficos/datos_box_vtas_ltrs_baseline.png) |
| vtas_ltrs_cualquier_promo | 0 | 186 | 186 | -279 … 465 | 2653 (17.7 %) | ![Boxplot de vtas_ltrs_cualquier_promo](graficos/datos_box_vtas_ltrs_cualquier_promo.png) |
| vtas_ltrs_sin_promo | 21.12 | 668.9 | 647.8 | -950.6 … 1641 | 2057 (13.7 %) | ![Boxplot de vtas_ltrs_sin_promo](graficos/datos_box_vtas_ltrs_sin_promo.png) |
| precio_ltrs_promedio | 2.186 | 3.535 | 1.349 | 0.1625 … 5.559 | 1064 (7.1 %) | ![Boxplot de precio_ltrs_promedio](graficos/datos_box_precio_ltrs_promedio.png) |
| precio_ltrs_cualquier_promo | 1.955 | 3.049 | 1.094 | 0.3136 … 4.691 | 657 (6.6 %) | ![Boxplot de precio_ltrs_cualquier_promo](graficos/datos_box_precio_ltrs_cualquier_promo.png) |
| precio_ltrs_sin_promo | 2.271 | 3.593 | 1.322 | 0.288 … 5.576 | 1049 (7.3 %) | ![Boxplot de precio_ltrs_sin_promo](graficos/datos_box_precio_ltrs_sin_promo.png) |
| vtas_valor | 105.9 | 3048 | 2942 | -4307 … 7460 | 1966 (13.1 %) | ![Boxplot de vtas_valor](graficos/datos_box_vtas_valor.png) |
| precio_ltrs_promedio_damm | 2.186 | 3.535 | 1.349 | 0.1625 … 5.559 | 1064 (7.1 %) | ![Boxplot de precio_ltrs_promedio_damm](graficos/datos_box_precio_ltrs_promedio_damm.png) |
| precio_ltrs_cualquier_promo_damm | 2.074 | 3.344 | 1.27 | 0.169 … 5.249 | 1103 (7.4 %) | ![Boxplot de precio_ltrs_cualquier_promo_damm](graficos/datos_box_precio_ltrs_cualquier_promo_damm.png) |
| precio_ltrs_sin_promo_damm | 2.261 | 3.6 | 1.339 | 0.2525 … 5.608 | 1084 (7.2 %) | ![Boxplot de precio_ltrs_sin_promo_damm](graficos/datos_box_precio_ltrs_sin_promo_damm.png) |
| porcen_descuento | 0 | 10.15 | 10.15 | -15.22 … 25.36 | 1058 (7.1 %) | ![Boxplot de porcen_descuento](graficos/datos_box_porcen_descuento.png) |
| porcen_descuento_competencia | 0 | 8.177 | 8.177 | -12.27 … 20.44 | 986 (6.6 %) | ![Boxplot de porcen_descuento_competencia](graficos/datos_box_porcen_descuento_competencia.png) |
| uplift_ltrs | 0 | 39.51 | 39.51 | -59.26 … 98.77 | 3117 (20.8 %) | ![Boxplot de uplift_ltrs](graficos/datos_box_uplift_ltrs.png) |
| intensidad_promocional_porcen | 0 | 34.12 | 34.12 | -51.19 … 85.31 | 1568 (10.5 %) | ![Boxplot de intensidad_promocional_porcen](graficos/datos_box_intensidad_promocional_porcen.png) |
| cuota_ltrs_total_mercado_end_we… | 0.005998 | 0.155 | 0.149 | -0.2175 … 0.3785 | 2150 (14.3 %) | ![Boxplot de cuota_ltrs_total_mercado_end_week](graficos/datos_box_cuota_ltrs_total_mercado_end_week.png) |
| cuota_valor_total_mercado_end_w… | 0.01013 | 0.204 | 0.1938 | -0.2806 … 0.4947 | 1954 (13.0 %) | ![Boxplot de cuota_valor_total_mercado_end_week](graficos/datos_box_cuota_valor_total_mercado_end_week.png) |

## 5. Gráficos

Rutas relativas a este informe, para que los PNG se vean en GitHub.

### Hoja `datos`


Distribución de categóricas:

![Distribución de marca](graficos/datos_bar_marca.png)

![Distribución de markets](graficos/datos_bar_markets.png)

![Distribución de sociedades](graficos/datos_bar_sociedades.png)

![Distribución de envase](graficos/datos_bar_envase.png)

![Distribución de unidades](graficos/datos_bar_unidades.png)

![Distribución de segmento](graficos/datos_bar_segmento.png)

Distribución de numéricas:

![Distribución de capacidad](graficos/datos_dist_capacidad.png)

![Distribución de vtas_ltrs](graficos/datos_dist_vtas_ltrs.png)

![Distribución de vtas_ltrs_baseline](graficos/datos_dist_vtas_ltrs_baseline.png)

![Distribución de vtas_ltrs_cualquier_promo](graficos/datos_dist_vtas_ltrs_cualquier_promo.png)

![Distribución de vtas_ltrs_sin_promo](graficos/datos_dist_vtas_ltrs_sin_promo.png)

![Distribución de precio_ltrs_promedio](graficos/datos_dist_precio_ltrs_promedio.png)

![Distribución de precio_ltrs_cualquier_promo](graficos/datos_dist_precio_ltrs_cualquier_promo.png)

![Distribución de precio_ltrs_sin_promo](graficos/datos_dist_precio_ltrs_sin_promo.png)

![Distribución de vtas_valor](graficos/datos_dist_vtas_valor.png)

![Distribución de precio_ltrs_promedio_damm](graficos/datos_dist_precio_ltrs_promedio_damm.png)

![Distribución de precio_ltrs_cualquier_promo_damm](graficos/datos_dist_precio_ltrs_cualquier_promo_damm.png)

![Distribución de precio_ltrs_sin_promo_damm](graficos/datos_dist_precio_ltrs_sin_promo_damm.png)

![Distribución de porcen_descuento](graficos/datos_dist_porcen_descuento.png)

![Distribución de porcen_descuento_competencia](graficos/datos_dist_porcen_descuento_competencia.png)

![Distribución de uplift_ltrs](graficos/datos_dist_uplift_ltrs.png)

![Distribución de intensidad_promocional_porcen](graficos/datos_dist_intensidad_promocional_porcen.png)

![Distribución de cuota_ltrs_total_mercado_end_week](graficos/datos_dist_cuota_ltrs_total_mercado_end_week.png)

![Distribución de cuota_valor_total_mercado_end_week](graficos/datos_dist_cuota_valor_total_mercado_end_week.png)

Matriz de correlación y relaciones más fuertes:

![Matriz de correlación de datos](graficos/datos_correlacion.png)

`precio_ltrs_promedio` y `precio_ltrs_promedio_damm`: r = 1.00.

![precio_ltrs_promedio frente a precio_ltrs_promedio_damm](graficos/datos_scatter_precio_ltrs_promedio_vs_precio_ltrs_promedio_damm.png)

`precio_ltrs_cualquier_promo` y `precio_ltrs_cualquier_promo_damm`: r = 1.00.

![precio_ltrs_cualquier_promo frente a precio_ltrs_cualquier_promo_damm](graficos/datos_scatter_precio_ltrs_cualquier_promo_vs_precio_ltrs_cualquier_promo_damm.png)

`precio_ltrs_sin_promo` y `precio_ltrs_sin_promo_damm`: r = 1.00.

![precio_ltrs_sin_promo frente a precio_ltrs_sin_promo_damm](graficos/datos_scatter_precio_ltrs_sin_promo_vs_precio_ltrs_sin_promo_damm.png)

`precio_ltrs_promedio` y `precio_ltrs_sin_promo_damm`: r = 0.99.

![precio_ltrs_promedio frente a precio_ltrs_sin_promo_damm](graficos/datos_scatter_precio_ltrs_promedio_vs_precio_ltrs_sin_promo_damm.png)

`precio_ltrs_promedio_damm` y `precio_ltrs_sin_promo_damm`: r = 0.99.

![precio_ltrs_promedio_damm frente a precio_ltrs_sin_promo_damm](graficos/datos_scatter_precio_ltrs_promedio_damm_vs_precio_ltrs_sin_promo_damm.png)

`precio_ltrs_promedio` y `precio_ltrs_sin_promo`: r = 0.99.

![precio_ltrs_promedio frente a precio_ltrs_sin_promo](graficos/datos_scatter_precio_ltrs_promedio_vs_precio_ltrs_sin_promo.png)

## 6. Conclusiones

La variable principal es `vtas_ltrs`: litros vendidos de cada referencia, en un mercado y una semana. La muestra tiene 15 000 filas, del 7 de enero al 29 de diciembre de 2024 (32 semanas), con 265 marcas, 11 mercados y 14 sociedades. No hay filas duplicadas.

### Hallazgos principales

- `vtas_ltrs` está muy concentrada. La mediana es 232,7 L y la media 3 301 L; el máximo llega a 959 480 L. El histograma queda en una sola barra porque el eje llega hasta ese máximo y casi todas las filas están en el primer tramo. El boxplot sitúa la caja entre 34 L y 1 207 L, con la valla superior del rango intercuartílico en 2 967 L.
- Esas 2 106 filas por encima de 2 967 L son el 14,0 % de la muestra y reúnen el 88,4 % de los litros. El 1 % de filas con más litros concentra el 45,5 % del volumen. Son las referencias grandes del sell-out, no colas que convenga borrar antes de sumar litros.
- Los litros se reconstruyen por identidades. `vtas_ltrs_cualquier_promo` + `vtas_ltrs_sin_promo` coincide con `vtas_ltrs`. `uplift_ltrs` coincide con `vtas_ltrs` − `vtas_ltrs_baseline`. En la matriz, las correlaciones altas con la variable principal son `vtas_valor` (r = 0,95), litros en promoción (r = 0,83), baseline (r = 0,76), uplift (r = 0,76), litros sin promoción (r = 0,71) y la cuota de litros (r = 0,63). El precio medio solo correlaciona −0,14 y la capacidad 0,02. Los scatterplots del informe son los pares de precios duplicados (r ≈ 1), no las relaciones comerciales de `vtas_ltrs`.
- La promoción aparece en el 66,8 % de las filas, pero la mediana de litros en promoción es el 4,6 % de los litros de la fila. La intensidad promocional correlaciona 0,15 con `vtas_ltrs`: las filas grandes también tienen muchos litros promocionales, y la parte promocional sigue siendo pequeña.
- El volumen no sigue a la frecuencia de filas. Mainstream tiene 3 558 filas y el 40,9 % de los litros; Premium tiene 5 511 filas y el 33,3 %. MDD tiene 220 filas, mediana 5 704 L y el 16,3 % de los litros (la marca `MARCAS DISTRI.`). La lata es el 73,6 % de los litros con mediana 442 L; la botella es la clase más frecuente y aporta el 26,4 %, con mediana 130 L. BTE y TORP suman 22 filas.
- Carrefour híper y Carrefour súper reúnen el 70,1 % de los litros. Eroski online (mediana 24 L) y Condisline (mediana 9 L) aportan muchas filas y muy poco volumen. `S.DAMM` es la sociedad con más filas (21,9 %) y el 11,6 % de los litros; dentro de Damm, Estrella Damm es la marca mayor de la muestra, con el 4,1 % del total de litros.
- Las cuotas de la misma semana y el mismo mercado suman 100. Están en puntos porcentuales: una mediana de 0,03 es una cuota del 0,03 %, no del 3 %.
- `capacidad` tiene IQR nulo porque el 50 % central es 330 ml (9 381 de 15 000 filas). Hay otros formatos, de 200 ml a 5 000 ml, así que la columna sí informa.

### Problemas de calidad de los datos

- `precio_ltrs_promedio_damm` es una copia exacta de `precio_ltrs_promedio`. Sigue en el CSV. Las otras columnas `*_damm` de precio coinciden con su par cuando las dos tienen valor; no son copias exactas, porque cubren los nulos del par original. `precio_ltrs_cualquier_promo` tiene 4 984 nulos (33,2 %), las filas sin litros en promoción. `precio_ltrs_sin_promo` tiene 549 nulos (3,7 %). En esos huecos, la versión `_damm` sí trae precio.
- Hay 21 filas con precio medio 0. `vtas_ltrs` no tiene ceros; el mínimo es 0,2 L. El 13,0 % de las filas vende por debajo de su baseline (uplift negativo).
- El segmento `Discount maisntream` está mal escrito y afecta a 619 filas. `unidades` llega como texto con ceros a la izquierda (`01`, `06`, `12`) y con el código `MD` en las marcas de distribuidor, el mismo bloque de 203 filas que concentra el 16,1 % de los litros.
- Los totales mensuales no describen la estacionalidad. Abril tiene 306 filas, una semana y un mercado; diciembre tiene 2 734 filas, cuatro semanas y cinco mercados. El máximo mensual es unas 40 veces el mínimo por ese desequilibrio de la muestra. La hoja `info` no tiene filas de documentación.

### Recomendaciones

- Analizar `vtas_ltrs` con la mediana y con el total de litros por separado. La media la arrastran unas pocas referencias. Para un modelo, usar escala logarítmica y no eliminar las 2 106 filas atípicas: son el grueso del volumen.
- No usar a la vez `vtas_ltrs`, sus dos componentes promocional y no promocional, ni baseline y uplift, como si fueran predictores independientes: unos reconstruyen a los otros.
- Confirmar el borrado solo de `precio_ltrs_promedio_damm`. Conservar `precio_ltrs_cualquier_promo_damm` y `precio_ltrs_sin_promo_damm`, que rellenan los precios ausentes. Hasta esa confirmación no se ha eliminado ninguna columna.
- Corregir `Discount maisntream` y tratar `unidades` como categoría, con `MD` aparte de los packs numéricos.
- Comparar mercados, segmentos y sociedades por litros totales, no por número de filas. Leer la cuota como puntos que suman 100 dentro de cada mercado y semana. No comparar meses sin tener en cuenta cuántas semanas y mercados entran en cada uno.
