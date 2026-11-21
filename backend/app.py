from flask import Flask, request, jsonify
from flask_cors import CORS
from database import guardar_simulacion, obtener_historial_simulaciones

app = Flask(__name__)
CORS(app)  # Permite peticiones desde el frontend

@app.route('/api/simular', methods=['POST'])
def api_simular():
    data = request.json
    escenario_id = data.get('escenario_id', 1)
    usuario_equipo = data.get('usuario_equipo', 'Integrante 4')
    ejecuciones = data.get('ejecuciones', [])
    
    sim_id = guardar_simulacion(escenario_id, usuario_equipo, ejecuciones)
    return jsonify({"status": "ok", "simulacion_id": sim_id, "mensaje": "Simulación guardada en BD"})

@app.route('/api/historial', methods=['GET'])
def api_historial():
    historial = obtener_historial_simulaciones()
    return jsonify({"status": "ok", "historial": historial})

if __name__ == '__main__':
    print("🚀 Servidor SIMTELE-RISK corriendo en http://localhost:5000")
    app.run(debug=True, port=5000)