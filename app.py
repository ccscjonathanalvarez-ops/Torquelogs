from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import logging
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app) # Habilita CORS para que Lovable pueda consultar la API

# Configuración del archivo de log
LOG_FILE = 'torque_data.jsonl'

# Configurar logging para escribir en un archivo y en la consola
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

@app.route('/')
def dashboard():
    """Sirve la interfaz HTML."""
    return render_template('index.html')

@app.route('/api/logs')
def get_logs():
    """Lee el archivo JSONL y devuelve los datos como JSON."""
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return jsonify(logs)

@app.route('/torque', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/torque/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    """
    Ruta que captura cualquier petición enviada al servidor.
    Torque Pro suele enviar datos por GET con múltiples parámetros.
    """
    # Recolectar todos los datos posibles
    data = {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "path": path,
        "args": request.args.to_dict(),
        "headers": dict(request.headers),
        "remote_addr": request.remote_addr
    }

    # Si hay cuerpo en la petición (POST), capturarlo también
    if request.is_json:
        data["body"] = request.json
    else:
        data["body"] = request.get_data(as_text=True)

    # Registrar los datos en formato JSON para facilitar su posterior análisis
    logging.info(json.dumps(data))
    
    print(f"\n[+] Nueva petición capturada en /{path}")
    print(f"    Parámetros: {json.dumps(request.args.to_dict(), indent=2)}")

    # Torque Pro espera la cadena "OK!" para confirmar que los datos se recibieron correctamente.
    return "OK!"

if __name__ == '__main__':
    print("Servidor de captura Torque Pro iniciado...")
    print(f"Los datos se guardarán en: {os.path.abspath(LOG_FILE)}")
    # Se recomienda usar un túnel como ngrok si se desea recibir datos desde internet (celular con Torque)
    app.run(host='0.0.0.0', port=5000, debug=True)
