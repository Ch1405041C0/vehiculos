from flask import Flask, abort, jsonify, render_template, request

from stock import StockCatalog

app = Flask(__name__)

# DEMO only. This will be replaced by the shared persistent DB used by web/app/backend.
VEHICLES = [
    {"id": 1, "brand": "Toyota", "model": "Corolla XEI 2.0", "year": 2022, "km": 45000, "transmission": "Automática", "fuel": "Nafta", "type": "Auto", "price": "$ 29.900.000", "tag": "DEMO", "features": ["Climatizador automático", "Cámara de retroceso"], "status": "PUBLICADO", "finances": True, "description": "Unidad demo para validar el circuito Machina.", "images": [], "videos": []},
    {"id": 2, "brand": "Volkswagen", "model": "Amarok Highline V6", "year": 2021, "km": 72000, "transmission": "Automática", "fuel": "Diésel", "type": "Pickup", "price": "$ 48.500.000", "tag": "DEMO", "features": ["4Motion", "Sensores de estacionamiento"], "status": "PUBLICADO", "finances": False, "description": "Unidad demo para validar el circuito Machina.", "images": [], "videos": []},
]

stock = StockCatalog(VEHICLES)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/buscar')
def search_flow():
    return render_template('search.html')


@app.route('/vehiculo/<int:vehicle_id>')
def vehicle(vehicle_id):
    item = stock.public_get(vehicle_id)
    if not item:
        abort(404)
    return render_template('vehicle.html', vehicle=item)


@app.route('/admin')
def admin():
    return render_template('admin.html', vehicles=stock.admin_list())


@app.get('/api/vehiculos')
def vehicles_api():
    # Transitional endpoint. Later the matching backend will decide which published units to return.
    return jsonify(stock.public_list(
        query=request.args.get('q', ''),
        vehicle_type=request.args.get('type', ''),
    ))


@app.get('/api/admin/stock')
def admin_stock_api():
    return jsonify(stock.admin_list())


@app.post('/api/admin/stock')
def admin_create_vehicle():
    return jsonify(stock.create(request.get_json(silent=True) or {})), 201


@app.patch('/api/admin/stock/<int:vehicle_id>')
def admin_update_vehicle(vehicle_id):
    item = stock.update(vehicle_id, request.get_json(silent=True) or {})
    if not item:
        abort(404)
    return jsonify(item)


@app.post('/api/admin/stock/<int:vehicle_id>/status')
def admin_change_status(vehicle_id):
    payload = request.get_json(silent=True) or {}
    try:
        item = stock.set_status(vehicle_id, payload.get('status', ''))
    except ValueError:
        return jsonify({"error": "Estado inválido"}), 400
    if not item:
        abort(404)
    return jsonify(item)


@app.delete('/api/admin/stock/<int:vehicle_id>')
def admin_delete_vehicle(vehicle_id):
    item = stock.delete(vehicle_id)
    if not item:
        abort(404)
    return '', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
