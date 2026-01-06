from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# 1. Cargar entorno y Configuración
load_dotenv()
IS_PROD = os.environ.get('RENDER') is not None

app = Flask(__name__, static_folder='dist', static_url_path='')
CORS(app)

# 2. Conexión a MySQL (PyMySQL)
user = "u659323332_mmq"
password = quote_plus("Mmq23456*")
host = "82.197.82.29"
port = 3306 # Aseguramos el puerto estándar
database = "u659323332_mmq"

# Añadimos el puerto a la URI
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 60,  # Reducimos el reciclaje para mantener la conexión fresca
    "connect_args": {
        "connect_timeout": 10 # Le damos 10 segundos para intentar conectar
    }
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 3. Modelos (Mantenlos para que SQLAlchemy no falle)
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(100))
    description = db.Column(db.Text)
    image = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    logo = db.Column(db.String(500))
    tier = db.Column(db.String(50))

# ==================== RUTAS DE LA API (EL ARREGLO) ====================

@app.route('/api/event-info', methods=['GET'])
def get_event_info():
    """Esta ruta es la que te da el error 404"""
    return jsonify({
        'status': 'success',
        'eventName': 'Media Maratón de Quibdó 2025',
        'eventDate': '2025-08-10T06:00:00'
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        events = Event.query.all()
        return jsonify({
            'status': 'success', 
            'events': [{'id': str(e.id), 'title': e.title, 'date': e.date, 'image': e.image} for e in events]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sponsors', methods=['GET'])
def get_sponsors():
    try:
        sponsors = Sponsor.query.all()
        return jsonify({
            'status': 'success', 
            'sponsors': [{'id': str(s.id), 'name': s.name, 'logo': s.logo, 'tier': s.tier} for s in sponsors]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== SERVIR FRONTEND & ERRORES ====================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Si la ruta existe en la carpeta dist (como css o js), la sirve
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # Si no, sirve el index.html para que React maneje la ruta
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith('/api/'):
        return jsonify({'status': 'error', 'message': 'API Route not found'}), 404
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Importante host='0.0.0.0' para Render
    app.run(host='0.0.0.0', port=port, debug=not IS_PROD)
