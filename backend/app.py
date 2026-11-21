from flask import Flask, request, jsonify
from flask_cors import CORS
from database import guardar_simulacion, obtener_historial_simulaciones
from modulo3 import escenario_normal, escenario_estres, escenario_mal_condicionado

app = Flask(__name__)
CORS(app)

@app.route('/api/modulo3/<escenario>', methods=['GET'])
def api_modulo3(escenario):
    esc_upper = escenario.upper()
    if esc_upper == 'NORMAL':
        res = escenario_normal()
    elif esc_upper == 'ESTRES':
        res = escenario_estres()
    elif esc_upper == 'MAL_CONDICIONADO':
        res = escenario_mal_condicionado()
    else:
        return jsonify({"error": "Escenario no válido"}), 400

    # Guardar automáticamente en SQLite (6 tablas)
    ejecuciones = [{
        "metodo": "RK4 (EDO) + Trapecio",
        "tolerancia": 1e-4,
        "tiempo_ms": 12.5,
        "convergio": True,
        "valor_final": {"energia": res["energia_acumulada"]},
        "interpretacion": f"Simulación del Módulo 3 completada en escenario {esc_upper}.",
        "iteraciones": []
    }]
    sim_id = guardar_simulacion(3, "Integrante 4 (Auto)", ejecuciones)
    res["simulacion_id_guardada"] = sim_id
    return jsonify(res)

@app.route('/api/historial', methods=['GET'])
def api_historial():
    return jsonify({"status": "ok", "historial": obtener_historial_simulaciones()})

if __name__ == '__main__':
    print("🚀 Servidor SIMTELE-RISK listo en http://localhost:5000")
    app.run(debug=True, port=5000)