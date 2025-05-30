import hashlib

from flask import Blueprint, request, jsonify, Flask

concilia_rest_bp = Blueprint('/concilia', __name__)
app = Flask(__name__)
app.config['DEBUG'] = True
import logging

import jwt
from datetime import datetime, timedelta
#import datetime
import json
from auth_router import checkValidityTokenByToken
from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from utils.utils import Utilities as utils
from conn.AppConnection import AppConnection
from utils.authHttpCodes import getHttpStatusDescription

app = Flask(__name__)
app.config['DEBUG'] = True
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
CORS(app)
dbConnection = AppConnection()


@concilia_rest_bp.route('/traer-conciliacion', methods=['POST'])
def getConciliacion():
    data = request.get_json()
    # logging.info("Datos recibidos: %s", data)
    if not data:
        control = {
            "codigo": 400,
            "estado": "Error",
            "mensaje": getHttpStatusDescription(400) + " | datos o parametros no recibidos.",
        }
        return jsonify({"control": control})

    # Extraer parámetros
    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    id_conciliacion = data.get('id_conciliacion')
    #logging.info("TOKEN VALIDO ??? --> "+checkValidityTokenByToken(token, userId))


    # Inicializa la conexión y el cursor
    if  checkValidityTokenByToken(token, userId):
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)


        # Verifica si el token es válido


        try:
            # Ejecutar el SELECT con los filtros
            sql = """
            SELECT * FROM SisMaster 
            WHERE idUsuario = %s AND idEmpresa = %s AND procesado_sn = 'N' and estado = 1 and idConcilia = %s and idUsuario = %s
            """
            cursor.execute(sql, (userId, clientId, id_conciliacion, userId))

            # Obtener los resultados y convertirlos en JSON
            resultados = cursor.fetchall()
            print(resultados)
            cantidad_movimientos = len(resultados)
            movimientos = []
            for row in resultados:
                movimiento = {
                    "idMaster": row["idMaster"],
                    "m_ingreso": row["m_ingreso"],
                    "pase": row["m_pase"],
                    "concepto": row["concepto"],
                    "comprobante": row["nro_comp"],
                    "detalle": row["detalle"],
                    "plan_cuenta": row["plan_cuentas"],
                    "asiento": row["m_asiento"],
                    "saldo": row["saldo"],
                    "codigo": row["codigo"],
                    "importe": row["importe"]
                }
                movimientos.append(movimiento)
            respuesta = {
                "control": {
                    "control": "OK",
                    "codigo": "200",
                    "mensaje": f"Se han encontrado {cantidad_movimientos} movimientos no conciliados.",
                },
                "datos": movimientos
            }
            respuesta_json = json.dumps(respuesta, default=str, ensure_ascii=False)
            print(respuesta_json)
            return respuesta_json
        except Exception as e:
            print(f"Error al ejecutar el SELECT: {e}")
            resultado_json = json.dumps({"error": str(e)})  # Devolver un error en JSON si algo falla
            respuesta = {
                "control": {
                    "control": "ERROR",
                    "codigo": "500",
                    "mensaje": f"Error al obtener datos de conciliación: {str(e)} "
                },
                "datos": []
            }
            respuesta_json = json.dumps(respuesta, default=str, ensure_ascii=False)
            print(respuesta_json)
            return respuesta_json

        finally:
            cursor.close()

    else:
        # Si el token no es válido, devolver un error
        respuesta = {
            "control": {
                "control": "ERROR",
                "codigo": "401",
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        }
        respuesta_json = json.dumps(respuesta, default=str, ensure_ascii=False)
        print(respuesta_json)
        return respuesta_json







@concilia_rest_bp.route('/traer-totales', methods=['POST'])
def getTotales():
    data = request.get_json()
    # logging.info("Datos recibidos: %s", data)
    if not data:
        control = {
            "codigo": 400,
            "estado": "Error",
            "mensaje": getHttpStatusDescription(400) + " | datos o parametros no recibidos.",
        }
        return jsonify({"control": control})

    # Extraer parámetros
    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    id_conciliacion = data.get('id_conciliacion')
    #logging.info("TOKEN VALIDO ??? --> "+checkValidityTokenByToken(token, userId))


    # Inicializa la conexión y el cursor
    if  checkValidityTokenByToken(token, userId):
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)


        # Verifica si el token es válido


        try:
            # Ejecutar el SELECT con los filtros
            sql = """
            SELECT * FROM SisMasterTotales
            WHERE idUsuario = %s AND idEmpresa = %s AND procesado_sn = 'N' and estado = 1 and idConcilia = %s and idUsuario = %s
            """
            cursor.execute(sql, (userId, clientId, id_conciliacion, userId))

            # Obtener los resultados y convertirlos en JSON
            resultados = cursor.fetchall()
            print(resultados)
            cantidad_movimientos = len(resultados)
            movimientos_tot = []

            for row in resultados:
                cuentaConcilia = resultados[0]["plan_cuentas"]
                movimiento = {
                    "idMaster": row["idMaster"],
                    "m_ingreso": row["m_ingreso"],
                    "asiento_concilia": row["m_asiento_concilia"],
                    "concepto": row["concepto"],
                    "plan_cuenta": row["plan_cuentas"],
                    "plan_cuenta_concilia": row["plan_cuentas_concilia"],
                    "importe": row["importe"],
                }
                movimientos_tot.append(movimiento)
            if movimientos_tot:
                respuesta = {
                    "control": {
                        "control": "OK",
                        "codigo": "200",
                        "mensaje": f"Se han encontrado {cantidad_movimientos} totales no conciliados.",
                    },
                    "datos": movimientos_tot
                }
            else:
                respuesta = {
                    "control": {
                        "control": "OK",
                        "codigo": "400",
                        "mensaje": f"No se encontraron movmientos.",
                    },
                    "datos": []
                }
            respuesta_json = json.dumps(respuesta, default=str, ensure_ascii=False)
            #print(respuesta_json)
            return respuesta_json
        except Exception as e:
            print(f"Error al ejecutar el SELECT: {e}")
            resultado_json = json.dumps({"error": str(e)})  # Devolver un error en JSON si algo falla
            respuesta = {
                "control": {
                    "control": "ERROR",
                    "codigo": "500",
                    "mensaje": f"Error al obtener datos de conciliación: {str(e)} "
                },
                "datos": []
            }
            respuesta_json = json.dumps(respuesta, default=str, ensure_ascii=False)
            print(respuesta_json)
            return respuesta_json

        finally:
            cursor.close()

    else:
        # Si el token no es válido, devolver un error
        respuesta = {
            "control": {
                "control": "ERROR",
                "codigo": "401",
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        }
        respuesta_json = json.dumps(respuesta, default=str, ensure_ascii=False)
        print(respuesta_json)
        return respuesta_json


@concilia_rest_bp.route('/traer-cuentas-contables', methods=['POST'])
def getCuentasContables():
    data = request.get_json()
    # logging.info("Datos recibidos: %s", data)
    if not data:
        control = {
            "codigo": 400,
            "estado": "Error",
            "mensaje": getHttpStatusDescription(400) + " | datos o parametros no recibidos.",
        }
        return jsonify({"control": control})

    # Extraer parámetros
    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')


    # Inicializa la conexión y el cursor
    if  checkValidityTokenByToken(token, userId):
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)


        # Verifica si el token es válido


        try:
            # Ejecutar el SELECT con los filtros
            sql = """
            SELECT * FROM PlanCuentas
            WHERE idEmpresa = %s  and estado = 1 order by orden asc
            """
            cursor.execute(sql, (clientId,))

            # Obtener los resultados y convertirlos en JSON
            resultados = cursor.fetchall()
            print(resultados)
            cantidad_movimientos = len(resultados)
            movimientos_tot = []
            for row in resultados:
                movimiento = {
                    "id": row["id"],
                    "plan_cuentas": row["plan_cuentas"],
                    "descripcion": row["descripcion"],
                    "orden" : row["orden"]

                }
                movimientos_tot.append(movimiento)
            if movimientos_tot:
                respuesta = {
                    "control": {
                        "control": "OK",
                        "codigo": "200",
                        "mensaje": f"Se han encontrado {cantidad_movimientos}.",
                    },
                    "datos": movimientos_tot
                }
            else:
                respuesta = {
                    "control": {
                        "control": "OK",
                        "codigo": "400",
                        "mensaje": f"No se encontraron movmientos.",
                    },
                    "datos": []
                }
            respuesta_json = json.dumps(respuesta, default=str, ensure_ascii=False)
            print(respuesta_json)
            return respuesta_json
        except Exception as e:
            print(f"Error al ejecutar el SELECT: {e}")
            resultado_json = json.dumps({"error": str(e)})  # Devolver un error en JSON si algo falla
            respuesta = {
                "control": {
                    "control": "ERROR",
                    "codigo": "500",
                    "mensaje": f"Error al obtener datos de conciliación: {str(e)} "
                },
                "datos": []
            }
            respuesta_json = json.dumps(respuesta, default=str, ensure_ascii=False)
            print(respuesta_json)
            return respuesta_json

        finally:
            cursor.close()

    else:
        # Si el token no es válido, devolver un error
        respuesta = {
            "control": {
                "control": "ERROR",
                "codigo": "401",
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        }
        respuesta_json = json.dumps(respuesta, default=str, ensure_ascii=False)
        print(respuesta_json)
        return respuesta_json


@concilia_rest_bp.route('/dummy', methods=['GET'])
def dummy():
    import json
    data = {
        "code": "1",
        "version": "1.0",
        "status": 200,
        "description": "Conciliacion.",
        "name": "Conciliacion Bancaria",
        "message": "Conciliacion Bancaria, servicio de conciliación funciona correctamente.",
        "functions": ["login", "recoverPassword", "logout"]
    }
    json_output = json.dumps(data, indent=4)
    logging.info(json_output)
    return json_output



