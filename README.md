# Vehículos · Demo comercial

Prototipo de catálogo digital para una empresa de venta de vehículos.

## Incluye
- Home comercial responsive.
- Catálogo demo de seis vehículos.
- Búsqueda por marca/modelo/año.
- Filtros Auto / SUV / Pickup.
- Ficha individual con características y equipamiento.
- CTA `ME INTERESA` y `HABLAR CON UN ASESOR` preparado para enviar el vehículo seleccionado a Chatbox.

Los vehículos, precios y datos actuales son ficticios y están identificados como DEMO.

## Ejecutar
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrir: `http://127.0.0.1:5100`

Chatbox puede mantenerse ejecutándose en `http://127.0.0.1:5000` durante las pruebas locales.

## Próximo paso
Integrar el contexto del vehículo con Chatbox para que el bot no vuelva a preguntar qué unidad interesa y crear administración de stock.