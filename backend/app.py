from flask import Flask, request, jsonify
from flask_cors import CORS
from database import guardar_simulacion, obtener_historial_simulaciones
from modulo3 import escenario_normal as mod3_normal, escenario_estres as mod3_estres, escenario_mal_condicionado as mod3_mal
from raices import simular_modulo1_raices, simular_modulo2_umbral

app = Flask(__name__)
CORS(app)

# -------------------------------------------------------------
# MÓDULO 1: Detención de Emergencia (Raíces)
# -------------------------------------------------------------
@app.route('/api/modulo1/<escenario>', methods=['GET'])
def api_modulo1(escenario):
    try:
        res = simular_modulo1_raices(escenario=escenario)
        ejecuciones = []
        for m in res["metodos"]:
            ejecuciones.append({
                "metodo": m["metodo"],
                "tolerancia": m["tolerancia"],
                "tiempo_ms": m["tiempo_ms"],
                "convergio": m["convergio"],
                "valor_final": {"raiz": m["raiz"], "motivo": m["motivo"]},
                "interpretacion": f"Tiempo de detención calculado en escenario {escenario.upper()}.",
                "iteraciones": m["iteraciones"]
            })
        sim_id = guardar_simulacion(1, "Integrante 1 + 4", ejecuciones)
        res["simulacion_id_guardada"] = sim_id
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# -------------------------------------------------------------
# MÓDULO 2: Deterioro y Umbral de Mantenimiento
# -------------------------------------------------------------
@app.route('/api/modulo2/umbral', methods=['GET'])
def api_modulo2():
    res = simular_modulo2_umbral()
    ejecuciones = []
    for m in res["metodos"]:
        ejecuciones.append({
            "metodo": m["metodo"],
            "tolerancia": m["tolerancia"],
            "tiempo_ms": m["tiempo_ms"],
            "convergio": m["convergio"],
            "valor_final": {"t_umbral_dias": m["raiz"]},
            "interpretacion": "Cruce de umbral de mantenimiento D(t) - D_umbral = 0.",
            "iteraciones": m["iteraciones"]
        })
    sim_id = guardar_simulacion(2, "Integrante 1 + 4", ejecuciones)
    res["simulacion_id_guardada"] = sim_id
    return jsonify(res)

# -------------------------------------------------------------
# MÓDULO 3: Oscilaciones por Viento (EDO e Integración)
# -------------------------------------------------------------
@app.route('/api/modulo3/<escenario>', methods=['GET'])
def api_modulo3(escenario):
    esc_upper = escenario.upper()
    if esc_upper == 'NORMAL':
        res = mod3_normal()
    elif esc_upper == 'ESTRES':
        res = mod3_estres()
    elif esc_upper == 'MAL_CONDICIONADO':
        res = mod3_mal()
    else:
        return jsonify({"error": "Escenario no válido"}), 400

    ejecuciones = [{
        "metodo": "RK4 (EDO) + Trapecio",
        "tolerancia": 1e-4,
        "tiempo_ms": 12.5,
        "convergio": True,
        "valor_final": {"energia": res["energia_acumulada"]},
        "interpretacion": f"Oscilaciones simuladas en escenario {esc_upper}.",
        "iteraciones": []
    }]
    sim_id = guardar_simulacion(3, "Integrante 2 + 4", ejecuciones)
    res["simulacion_id_guardada"] = sim_id
    return jsonify(res)

@app.route('/api/historial', methods=['GET'])
def api_historial():
    return jsonify({"status": "ok", "historial": obtener_historial_simulaciones()})

if __name__ == '__main__':
    print("🚀 Servidor SIMTELE-RISK activo en http://localhost:5000")
    app.run(debug=True, port=5000)