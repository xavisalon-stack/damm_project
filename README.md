# proyectos_damm
repo con los datos en excel para ser usados con cursor agent en los proyectos de Damm

## Experiencias web

Los HTML de preventa y consumidor están en `web/`. Para verlos localmente:

```bash
python3 -m http.server 4173 --directory web
```

Después, abrir `http://localhost:4173`. Los datos agregados de `web/datos.js` se
pueden regenerar desde los Excel originales con:

```bash
python3 scripts/generar_datos_web.py
```
