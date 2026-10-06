from flask import Flask, abort, jsonify, render_template, request

from matcher import VehiclePreferences, profile_vehicle, rank_vehicles

app = Flask(__name__)

VEHICLES = [
    {"id":1,"brand":"Toyota","model":"Corolla XEI 2.0","year":2022,"km":45000,"transmission":"Automática","fuel":"Nafta","type":"Auto","price":"$ 29.900.000","tag":"Oportunidad","image":"https://images.unsplash.com/photo-1623869675781-80aa31012a5a?auto=format&fit=crop&w=1200&q=80","features":["Climatizador automático","Cámara de retroceso","Control de velocidad crucero","Pantalla multimedia","Control de estabilidad","6 airbags"]},
    {"id":2,"brand":"Volkswagen","model":"Amarok Highline V6","year":2021,"km":72000,"transmission":"Automática","fuel":"Diésel","type":"Pickup","price":"$ 48.500.000","tag":"Destacada","image":"https://images.unsplash.com/photo-1551830820-330a71b99659?auto=format&fit=crop&w=1200&q=80","features":["4Motion","Tapizado de cuero","Sensores de estacionamiento","Climatizador bi-zona","Control crucero","Llantas de aleación"]},
    {"id":3,"brand":"Ford","model":"Territory Titanium","year":2023,"km":28000,"transmission":"Automática","fuel":"Nafta","type":"SUV","price":"$ 38.700.000","tag":"Ingreso reciente","image":"https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?auto=format&fit=crop&w=1200&q=80","features":["Techo panorámico","Cámara 360°","Asientos eléctricos","ADAS","CarPlay / Android Auto","Acceso sin llave"]},
    {"id":4,"brand":"Chevrolet","model":"Cruze Premier","year":2022,"km":39000,"transmission":"Automática","fuel":"Nafta","type":"Auto","price":"$ 27.800.000","tag":"","image":"https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=80","features":["Wi-Fi","Climatizador","Cámara trasera","Control crucero","Tapizado de cuero","Alerta de punto ciego"]},
    {"id":5,"brand":"Jeep","model":"Renegade Longitude","year":2021,"km":61000,"transmission":"Automática","fuel":"Nafta","type":"SUV","price":"$ 25.900.000","tag":"","image":"https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=80","features":["Control de estabilidad","Multimedia","Cámara trasera","Climatizador","Llantas de aleación","Control crucero"]},
    {"id":6,"brand":"Peugeot","model":"208 Feline","year":2023,"km":19000,"transmission":"Automática","fuel":"Nafta","type":"Auto","price":"$ 24.600.000","tag":"Bajo kilometraje","image":"https://images.unsplash.com/photo-1542362567-b07e54358753?auto=format&fit=crop&w=1200&q=80","features":["i-Cockpit","Techo panorámico","Climatizador","Cámara 180°","CarPlay / Android Auto","Sensores traseros"]}
]


def _vehicle_with_profile(vehicle: dict) -> dict:
    return {**vehicle, "profile": profile_vehicle(vehicle)}


@app.route('/')
def home():
    return render_template('index.html', vehicles=[_vehicle_with_profile(v) for v in VEHICLES])


@app.route('/vehiculo/<int:vehicle_id>')
def vehicle(vehicle_id):
    item = next((v for v in VEHICLES if v['id'] == vehicle_id), None)
    if not item:
        abort(404)
    return render_template('vehicle.html', vehicle=_vehicle_with_profile(item))


@app.get('/api/vehiculos')
def vehicles_api():
    q = request.args.get('q', '').lower()
    kind = request.args.get('type', '').lower()
    data = [
        _vehicle_with_profile(v)
        for v in VEHICLES
        if (not q or q in f"{v['brand']} {v['model']} {v['year']}".lower())
        and (not kind or kind == 'todos' or v['type'].lower() == kind)
    ]
    return jsonify(data)


@app.post('/api/recomendaciones')
def recommendations_api():
    data = request.get_json(silent=True) or {}
    preferences = VehiclePreferences(
        vehicle_types=tuple(str(item) for item in data.get('types', []) if str(item).strip()),
        transmission=str(data.get('transmission', '')).strip(),
        fuel=str(data.get('fuel', '')).strip(),
        priorities=tuple(str(item) for item in data.get('priorities', []) if str(item).strip()),
        usage=str(data.get('usage', '')).strip(),
    )
    by_id = {vehicle['id']: vehicle for vehicle in VEHICLES}
    ranked = rank_vehicles(VEHICLES, preferences)
    results = []
    for match in ranked:
        vehicle = by_id[match.vehicle_id]
        results.append({
            'vehicle': _vehicle_with_profile(vehicle),
            'score': match.score,
            'reasons': list(match.reasons),
        })
    return jsonify({'results': results})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
