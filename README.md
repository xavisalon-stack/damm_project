# proyectos_damm
repo con los datos en excel para ser usados con cursor agent en los proyectos de Damm

## Prototipos Smart Replenishment

La carpeta `prototipos/` contiene dos propuestas navegables y responsive:

- `preventa.html`: priorización de oportunidades, nivel de confianza, detalle de la reposición y preparación del mensaje de WhatsApp.
- `cliente.html`: experiencia para el establecimiento, con ajuste de cantidades, resumen, confirmación o aplazamiento.

Para verlas localmente:

```bash
python3 -m http.server 4173 --directory prototipos
```

Después, abrir `http://localhost:4173/preventa.html` o `http://localhost:4173/cliente.html`.

Los establecimientos, segmentos, materiales y patrones de compra mostrados se inspiran en `ventas_sample.xlsx`, `dim_establecimiento_sample.xlsx` y `ca_pedidos_sample.xlsx`. Las predicciones, puntuaciones de confianza e importes de propuesta son simulaciones de interfaz y no salidas de un modelo entrenado.
