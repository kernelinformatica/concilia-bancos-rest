import logging
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from conn.AppConnection import AppConnection
from auth_router import auth_bp, dummy, login
from concilia_router import concilia_rest_bp, getAbmCuentasContables
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AppConciliaRest(AppConnection):
    def __init__(self):
        super().__init__()
        self.app = Flask(__name__)
        CORS(self.app)

        self.app.register_blueprint(auth_bp, url_prefix='/api/auth')
        self.app.register_blueprint(concilia_rest_bp, url_prefix='/api/concilia')

    def run(self, debug=True, host="0.0.0.0", port=5000):
        self.app.run(debug=True, host=host, port=port)

# **🚀 Ejecutar el servidor Flask**

if __name__ == "__main__":
    concilia = AppConciliaRest()
    try:
        with concilia.app.app_context():
            concilia.run(debug=True, port=5050)

    except Exception as e:
        logging.error(f"Error al iniciar el servicio: {e}")




"""
if __name__ == "__main__":
    app = AppConciliaRest()

    try:
        with app.app.test_request_context(
            '/concilia/cuentas-contables-abm',  # Ruta del endpoint
            method='POST',  # Método HTTP
            json={  # Datos de prueba
                "abm": "1",
                "cuenta": '{id: 0, tipo_cuenta: "2", descripcion: "Dar", plan_cuentas: "46545646546546"}',
                "id_conciliacion": "1",
                "id_empresa": 2,
                "id_usuario": 1,
                "token": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZFVzdWFyaW9zIjoxLCJleHAiOjE3NDk5MjcyMzV9.D71pWmuZKVn9AnKy1yT-arD2lOvZvyfd5-UzvKeobVk',
            }
        ):
            res = getAbmCuentasContables()
            print(res)

    except Exception as e:
        logging.error(f"Error al iniciar el servicio: {e}")
"""