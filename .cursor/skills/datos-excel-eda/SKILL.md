---
name: datos-excel-eda
description: >-
  Hace un análisis exploratorio de datos (EDA) de un fichero Excel y genera un
  informe Markdown con gráficos PNG y CSV. Usar cuando el usuario pida
  analizar, explorar o hacer un EDA de un Excel, un .xlsx o ficheros en datos/.
---

# EDA de Excel

Los Excel están en `datos/`. No modificar nunca los originales.

Los resultados se guardan en `eda/<nombre_fichero>_eda/`: un informe `informe_eda.md`, los gráficos en PNG enlazados con rutas relativas (para que se vean en GitHub) y los datos limpios en CSV.

Ejecutar el script de esta skill. No reimplementar el EDA en un notebook ni en código suelto, y no escribir el informe a mano salvo la sección de conclusiones.

## Cuándo usarla

Cuando el usuario pida analizar, explorar o hacer un EDA de un Excel.

## Procedimiento

1. Trabajar desde la raíz del repositorio. Si no existe el paquete, instalar dependencias:

```bash
python -m pip install -r .cursor/skills/datos-excel-eda/requirements.txt
```

2. Elegir el fichero dentro de `datos/`. Si el usuario no lo nombra y hay varios, preguntar cuál antes de calcular. Si pide todos, lanzar un comando por fichero: cada uno tiene su carpeta `eda/<nombre_fichero>_eda/`.

3. No eliminar columnas sin confirmación del usuario. No pasar `--excluir-columnas` ni `--eliminar-duplicados` salvo que en este encargo haya confirmado esas eliminaciones con nombres concretos. Esas opciones solo afectan al CSV y al cálculo de esa ejecución; el Excel de `datos/` sigue igual.

4. Generar el informe:

```bash
python .cursor/skills/datos-excel-eda/scripts/eda_excel.py datos/<nombre_fichero>.xlsx
```

Con confirmación explícita:

```bash
python .cursor/skills/datos-excel-eda/scripts/eda_excel.py datos/<nombre_fichero>.xlsx \
  --excluir-columnas ColA,ColB --eliminar-duplicados
```

5. Abrir `eda/<nombre_fichero>_eda/informe_eda.md` y los PNG de las relaciones y de los atípicos. Reescribir la sección `## 6. Conclusiones` en español y borrar la cita que la marca como borrador. Mantener estas tres subsecciones, con juicios concretos sobre este fichero (no frases genéricas):

- Hallazgos principales
- Problemas de calidad de los datos
- Recomendaciones

6. Comprobar que cada imagen del Markdown existe y usa una ruta relativa:

```bash
python .cursor/skills/datos-excel-eda/scripts/eda_excel.py --comprobar-informe eda/<nombre_fichero>_eda/informe_eda.md
```

7. Responder con la ruta del informe, los hallazgos y las columnas que se propone quitar. Recordar que no se han quitado si el usuario no lo confirmó.

## Qué debe contener el EDA

1. Vista general: hojas, filas, columnas y primeras filas.
2. Tipos de variables: numéricas (con estadísticas básicas) y categóricas (con número de clases).
3. Limpieza: duplicados, nulos y columnas poco útiles. Proponer qué eliminar, pero no eliminar columnas sin confirmación del usuario.
4. Valores atípicos con boxplots y criterio del rango intercuartílico.
5. Gráficos: distribución de categóricas y numéricas, matriz de correlación y scatterplots de las relaciones más fuertes.
6. Conclusiones en español: hallazgos principales, problemas de calidad de los datos y recomendaciones.

El script cubre los puntos 1 a 5 y deja el punto 6 como borrador numérico. Las conclusiones finales las escribe el agente después de mirar los gráficos.

## Criterios que aplica el script

- Hoja solo de vista general (sin gráficos ni CSV): nombre `info`, `metadata`, `metadatos`, `diccionario`, `readme` o `leeme`, o bien 2 columnas o menos y 5 filas o menos. `--incluir-hojas Nombre` fuerza el EDA de esa hoja.
- Limpieza aplicada siempre, solo sobre la copia: recortar nombres y textos, y pasar a nulo los textos vacíos y el marcador `#`. No se borran columnas ni filas duplicadas sin las opciones de confirmación.
- Columna poco útil (propuesta, no borrada): todo nulos o 95 % o más de nulos; un solo valor; copia exacta de otra columna; posible identificador (entero con un valor distinto por fila, o texto con al menos el 95 % de valores distintos y 20 filas o más). Una fecha con un solo valor se señala como periodo de la muestra.
- Esos posibles identificadores se tabulan y se proponen para eliminar, y se dejan fuera de histogramas, boxplots, correlación y scatter. Siguen en el CSV.
- Numérica con 15 valores distintos o menos: se anota como baja cardinalidad y su distribución es un diagrama de barras. El resto de numéricas lleva histograma.
- Atípicos: por debajo de Q1 − 1,5·IQR o por encima de Q3 + 1,5·IQR, con todas las filas. Si el IQR es 0, el criterio no aplica. El boxplot usa como máximo 20 000 filas muestreadas y oculta los puntos sueltos cuando hay más de 200 atípicos; el recuento de la tabla usa el fichero entero.
- Correlación de Pearson entre numéricas que no son identificadores. Scatterplots de hasta 6 pares con |r| ≥ 0,4; si no hay ninguno, el par más fuerte si |r| ≥ 0,2. Como máximo 4 000 puntos muestreados por scatter.
- Categórica con un valor distinto en cada fila no nula: se informa el número de clases y no se dibuja la barra.
- Enlaces de imagen relativos a `informe_eda.md`, con barras `/`, dentro de `graficos/`.
- CSV: `datos_limpios.csv` si hay una sola hoja analizada; `datos_limpios_<hoja>.csv` si hay varias.

## Entrega

No dar por cerrado el encargo con el borrador automático de conclusiones. No commitear la carpeta `eda/` salvo que el usuario pida versionar ese informe.
