import logging
import jwt
import os
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS
from dotenv import load_dotenv
from utils.utils import Utilities as utils
from conn.AppConnection import AppConnection
from utils.authHttpCodes import getHttpStatusDescription
from auth_router import checkValidityTokenByToken

# Configuración inicial
concilia_rest_bp = Blueprint('/concilia', __name__)
app = Flask(__name__)
app.config['DEBUG'] = True
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
CORS(app)
dbConnection = AppConnection()

# Función para cerrar conexiones de forma segura
def close_connection(cursor, connection):
    if cursor:
        cursor.close()
    if connection:
        connection.close()

# Ruta: traer-conciliacion
@concilia_rest_bp.route('/traer-conciliacion', methods=['POST'])
def getConciliacion():
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    id_conciliacion = data.get('id_conciliacion')
    estado = data.get('estado', 1)  # Por defecto, estado = 1 (activo), estado = 4 (No Conciliado)

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)

        sql = """
        SELECT * FROM SisMaster
        WHERE idUsuario = %s AND idEmpresa = %s AND  procesado_sn = 'N' and  idConcilia = %s and estado = %s
        """
        cursor.execute(sql, (userId, clientId, id_conciliacion,estado))
        resultados = cursor.fetchall()

        movimientos = [
            {
                "id_master": row["idMaster"],
                "id_cab_concilia": row["idCabConcilia"],
                "m_ingreso": row["m_ingreso"],
                "asiento_concilia": row["m_asiento_concilia"],
                "pase": row["m_pase"],
                "concepto": row["concepto"],
                "comprobante": row["nro_comp"],
                "comprobante_asoc": row["nro_comp_asoc"],
                "detalle": row["detalle"],
                "plan_cuenta": row["plan_cuentas"],
                "asiento": row["m_asiento"],
                "saldo": row["saldo"],
                "codigo": row["codigo"],
                "cuit": row["cuit"],
                "importe": row["importe"]
            }
            for row in resultados
        ]

        return jsonify({
            "control": {
                "control": "OK",
                "codigo": "200",
                "mensaje": f"Se han encontrado {len(movimientos)} movimientos no conciliados.",
            },
            "datos": movimientos
        })
    except Exception as e:
        logging.error(f"Error al ejecutar el SELECT: {e}")
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": "500",
                "mensaje": f"Error al obtener datos de conciliación: {str(e)}"
            },
            "datos": []
        })
    finally:
        close_connection(cursor, dbConnection.conn)

@concilia_rest_bp.route('/traer-dif-entidad-empresa', methods=['POST'])
def getDiferenciasEntidadEmpresa():
    #dario
    logging.info(":::::::::::::::::::: getDiferenciasEntidadEmpresa ::::::::::::::::::::::::")
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    id_conciliacion = data.get('id_conciliacion')

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)

        sql = """
        SELECT * FROM SisMaster
        WHERE idUsuario = %s AND idEmpresa = %s AND procesado_sn = 'N' AND estado = 5 AND idConcilia = %s
        """
        logging.info(str(sql))
        cursor.execute(sql, (userId, clientId, id_conciliacion))
        resultados = cursor.fetchall()

        movimientos_dif = [
            {
                "idMaster": row["idMaster"],
                "m_ingreso": row["m_ingreso"],
                "asiento_concilia": row["m_asiento_concilia"],
                "concepto": row["concepto"],
                "nro_comp": row["nro_comp"],
                "m_asiento": row["m_asiento"],
                "id_concilia": row["idConcilia"],
                "plan_cuenta": row["plan_cuentas"],
                "padron_codigo": row["padron_codigo"],
                "detalle": row["detalle"],
                "plan_cuenta_concilia": 0,
                "importe": row["importe"],
                "c4": 0,
            }
            for row in resultados
        ]

        mensaje = f"Se han encontrado {len(movimientos_dif)} totales no conciliados." if movimientos_dif else "No se encontraron movimientos."
        return jsonify({
            "control": {
                "control": "OK",
                "codigo": "200" if movimientos_dif else "400",
                "mensaje": mensaje,
            },
            "datos": movimientos_dif
        })
    except Exception as e:
        logging.error(f"Error al ejecutar el SELECT: {e}")
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": "500",
                "mensaje": f"Error al obtener datos de conciliación: {str(e)}"
            },
            "datos": []
        })
    finally:
        close_connection(cursor, dbConnection.conn)

@concilia_rest_bp.route('/traer-dif-empresa-entidad', methods=['POST'])
def getDiferenciasEmpresaEntidad():
    print(":::::::::::::::::::: getDiferenciasEmpresaEntidad")
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    id_conciliacion = data.get('id_conciliacion')

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)

        sql = """
        SELECT * FROM SisMasterEmpresa
        WHERE idUsuario = %s AND idEmpresa = %s AND procesado_sn = 'N' AND estado = 1 AND idConcilia = %s
        """
        cursor.execute(sql, (userId, clientId, id_conciliacion))
        resultados = cursor.fetchall()

        movimientos_dif = [
            {
                "idMaster": row["idMaster"],
                "m_ingreso": row["m_ingreso"],
                "asiento_concilia": row["m_asiento_concilia"],
                "concepto": row["concepto"],
                "nro_comp": row["nro_comp"],
                "m_asiento": row["m_asiento"],
                "plan_cuenta": row["plan_cuentas"],
                "padron_codigo": row["padron_codigo"],
                "detalle": row["detalle"],
                "plan_cuenta_concilia": row["plan_cuentas_concilia"],
                "importe": row["importe"],
                "c4": row["c4"],
            }
            for row in resultados
        ]

        mensaje = f"Se han encontrado {len(movimientos_dif)} totales no conciliados." if movimientos_dif else "No se encontraron movimientos."
        return jsonify({
            "control": {
                "control": "OK",
                "codigo": "200" if movimientos_dif else "400",
                "mensaje": mensaje,
            },
            "datos": movimientos_dif
        })
    except Exception as e:
        logging.error(f"Error al ejecutar el SELECT: {e}")
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": "500",
                "mensaje": f"Error al obtener datos de conciliación: {str(e)}"
            },
            "datos": []
        })
    finally:
        close_connection(cursor, dbConnection.conn)




@concilia_rest_bp.route('/traer-totales', methods=['POST'])
def getTotales():
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    id_conciliacion = data.get('id_conciliacion')

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)

        sql = """SELECT s.*, p.padron_codigo
FROM SisMasterTotales s
INNER JOIN PlanCuentas p
  ON p.plan_cuentas = s.plan_cuentas_concilia
  AND p.tipo_cuenta = 1
  AND p.idEmpresa = s.idEmpresa
WHERE s.idUsuario = %s 
  AND s.idEmpresa = %s 
  AND s.procesado_sn = 'N'
  AND s.estado = 1
  AND s.idConcilia = %s;
"""


        cursor.execute(sql, (userId, clientId, id_conciliacion))
        resultados = cursor.fetchall()

        movimientos_tot = [
            {
                "idMaster": row["idMaster"],
                "m_ingreso": row["m_ingreso"],
                "asiento_concilia": row["m_asiento_concilia"],
                "concepto": row["concepto"],
                "id_concilia": row["idConcilia"],
                "plan_cuenta": row["plan_cuentas"],
                "padron_codigo_cta_concilia": row["padron_codigo"],
                "plan_cuenta_concilia": row["plan_cuentas_concilia"],
                "importe": row["importe"],
            }
            for row in resultados
        ]

        mensaje = f"Se han encontrado {len(movimientos_tot)} totales no conciliados." if movimientos_tot else "No se encontraron movimientos."
        return jsonify({
            "control": {
                "control": "OK",
                "codigo": "200" if movimientos_tot else "400",
                "mensaje": mensaje,
            },
            "datos": movimientos_tot
        })
    except Exception as e:
        logging.error(f"Error al ejecutar el SELECT: {e}")
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": "500",
                "mensaje": f"Error al obtener datos de conciliación: {str(e)}"
            },
            "datos": []
        })
    finally:
        close_connection(cursor, dbConnection.conn)





@concilia_rest_bp.route('/traer-cuentas-contables-tipos', methods=['POST'])
def getCuentasContablesTipos():
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)
        sql = """
            select idTipo, nombre, descripcion from PlanCuentasTipos where estado = 1 order by idTipo asc
            """
        cursor.execute(sql)
        resultados = cursor.fetchall()
        # agregar que traiga los tipos de cuentas y los ponga en el movmientos_tot
        tipos = [
            {
                "id": row["idTipo"],
                "nombre": row["nombre"],
                "descripcion": row["descripcion"],

            }
            for row in resultados
        ]

        mensaje = f"Se han encontrado {len(tipos)}." if tipos else "No se encontraron cuentas."
        return jsonify({
            "control": {
                "control": "OK",
                "codigo": "200" if tipos else "400",
                "mensaje": mensaje,
            },
            "datos": tipos
        })
    except Exception as e:
        logging.error(f"Error al ejecutar el SELECT: {e}")
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": "500",
                "mensaje": f"Error al traertipos de cuenta contables: {str(e)}"
            },
            "datos": []
        })
    finally:
        close_connection(cursor, dbConnection.conn)



@concilia_rest_bp.route('/traer-cuentas-contables', methods=['POST'])
def getCuentasContables():
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    id_tipo = data.get('id_tipo', 0)  # Por defecto, 0 para todos los tipos de cuentas
    id_cuenta = data.get('id_cuenta', 0)  # Por defecto, 0 para todas las cuentas

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)

        if id_tipo == 0:

            if id_cuenta == 0 or id_cuenta is None:

                sql = """ SELECT PlanCuentas.id, PlanCuentas.tipo_cuenta, PlanCuentasTipos.nombre as tipo_cuenta_nombre, PlanCuentas.plan_cuentas, PlanCuentas.descripcion, PlanCuentas.orden , PlanCuentas.padron_codigo
                    FROM PlanCuentas, PlanCuentasTipos WHERE idEmpresa = %s AND PlanCuentas.estado = 1
                    and PlanCuentas.tipo_cuenta = PlanCuentasTipos.idTipo order by PlanCuentasTipos.idTipo, PlanCuentas.id asc """
                cursor.execute(sql, (clientId,))
            else:

                sql = """ SELECT PlanCuentas.id, PlanCuentas.tipo_cuenta, PlanCuentasTipos.nombre as tipo_cuenta_nombre, PlanCuentas.plan_cuentas, PlanCuentas.descripcion, PlanCuentas.orden , PlanCuentas.padron_codigo
                                    FROM PlanCuentas, PlanCuentasTipos WHERE idEmpresa = %s AND PlanCuentas.estado = 1 and PlanCuentas.id = %s
                                    and PlanCuentas.tipo_cuenta = PlanCuentasTipos.idTipo order by PlanCuentasTipos.idTipo, PlanCuentas.id asc """
                cursor.execute(sql, (clientId, id_cuenta,))
        else:
            if id_cuenta == 0 or id_cuenta is None:
                sql = """
                SELECT PlanCuentas.id, PlanCuentas.tipo_cuenta, PlanCuentasTipos.nombre as tipo_cuenta_nombre, PlanCuentas.plan_cuentas, PlanCuentas.descripcion, PlanCuentas.orden , PlanCuentas.padron_codigo
    FROM PlanCuentas, PlanCuentasTipos WHERE idEmpresa = %s AND PlanCuentas.estado = 1  and  tipo_cuenta = %s
    and PlanCuentas.tipo_cuenta = PlanCuentasTipos.idTipo  ORDER BY orden ASC
                """
                cursor.execute(sql, (clientId, id_tipo))
            else:
                sql = """SELECT PlanCuentas.id, PlanCuentas.tipo_cuenta, PlanCuentasTipos.nombre as tipo_cuenta_nombre, PlanCuentas.plan_cuentas, PlanCuentas.descripcion, PlanCuentas.orden , PlanCuentas.padron_codigo
                    FROM PlanCuentas, PlanCuentasTipos WHERE idEmpresa = %s AND PlanCuentas.estado = 1  and  tipo_cuenta = %s and PlanCuentas.id = %s
                    and PlanCuentas.tipo_cuenta = PlanCuentasTipos.idTipo  ORDER BY orden ASC
                                """

                cursor.execute(sql, (clientId, id_tipo, id_cuenta,))

        resultados = cursor.fetchall()
        # agregar que traiga los tipos de cuentas y los ponga en el movmientos_tot
        movimientos_tot = [
            {
                "id": row["id"],
                "plan_cuentas": row["plan_cuentas"],
                "descripcion": row["descripcion"],
                "tipo_cuenta_id": row["tipo_cuenta"],
                "tipo_cuenta_nombre": row["tipo_cuenta_nombre"],
                "padron_codigo": row["padron_codigo"],
                "orden": row["orden"]
            }
            for row in resultados
        ]

        mensaje = f"Se han encontrado {len(movimientos_tot)}." if movimientos_tot else "No se encontraron movimientos."
        return jsonify({
            "control": {
                "control": "OK",
                "codigo": "200" if movimientos_tot else "400",
                "mensaje": mensaje,
            },
            "datos": movimientos_tot
        })
    except Exception as e:
        logging.error(f"Error al ejecutar el SELECT: {e}")
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": "500",
                "mensaje": f"Error al obtener datos de conciliación: {str(e)}"
            },
            "datos": []
        })
    finally:
        close_connection(cursor, dbConnection.conn)


@concilia_rest_bp.route('/traer-cuentas-contables-empresa', methods=['POST'])
def getCuentasContablesEmpresa():
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)

        sql = """
        SELECT * FROM PlanCuentas
        WHERE idEmpresa = %s AND estado = 1 and tipo_cuenta = 1 ORDER BY orden ASC
        """
        cursor.execute(sql, (clientId,))
        resultados = cursor.fetchall()

        movimientos_tot = [
            {
                "id": row["id"],
                "plan_cuentas": row["plan_cuentas"],
                "descripcion": row["descripcion"],
                "orden": row["orden"]
            }
            for row in resultados
        ]

        mensaje = f"Se han encontrado {len(movimientos_tot)}." if movimientos_tot else "No se encontraron movimientos."
        return jsonify({
            "control": {
                "control": "OK",
                "codigo": "200" if movimientos_tot else "400",
                "mensaje": mensaje,
            },
            "datos": movimientos_tot
        })
    except Exception as e:
        logging.error(f"Error al ejecutar el SELECT: {e}")
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": "500",
                "mensaje": f"Error al obtener datos de conciliación: {str(e)}"
            },
            "datos": []
        })
    finally:
        close_connection(cursor, dbConnection.conn)






# Abm Preferencias
@concilia_rest_bp.route('/preferencias-traer', methods=['POST'])
def getPreferencias():
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            },
            "datos": []
        })

    clientId = data.get('id_empresa')
    if not clientId:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": "id_empresa no recibido."
            },
            "datos": []
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)

        sql = """SELECT plan_cuenta_concilia, plan_cuentas, detalle, concepto
                 FROM SisMasterTotalesGuarda
                 WHERE idEmpresa = %s AND estado = 1"""
        cursor.execute(sql, (clientId,))
        resultados = cursor.fetchall()

        return jsonify({
            "control": {
                "codigo": 200,
                "estado": "OK",
                "mensaje": getHttpStatusDescription(200) + " | Listado de preferencias por empresa.",
            },
            "datos": resultados
        })

    except Exception as e:
        logging.error(f"Error al ejecutar SELECT: {e}")
        return jsonify({
            "control": {
                "codigo": 500,
                "estado": "Error",
                "mensaje": f"Error al traer preferencias: {str(e)}"
            },
            "datos": []
        })
    finally:
        close_connection(cursor, dbConnection.conn)



@concilia_rest_bp.route('/preferencias-abm', methods=['POST'])

def getAbmPreferencias():

    data = request.get_json()

    # ============================================================
    # VALIDAR DATOS RECIBIDOS
    # ============================================================

    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) +
                           " | datos o parámetros no recibidos."
            },
            "datos": []
        }), 400

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    registros = data.get('preferencias_registros', [])
    accion = data.get('abm', 1)

    # ============================================================
    # VALIDAR REGISTROS
    # ============================================================

    if not registros:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": "No se recibieron registros de preferencias."
            },
            "datos": []
        }), 400

    # ============================================================
    # VALIDAR TOKEN
    # ============================================================

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "codigo": 401,
                "estado": "Error",
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        }), 401

    cursor = None

    # ============================================================
    # RESULTADOS
    # ============================================================

    insertadas = []
    ya_existentes = []
    eliminadas = []
    modificadas = []
    errores = []

    try:

        dbConnection.conn.connect()

        cursor = dbConnection.conn.cursor(dictionary=True)

        # ========================================================
        # PROCESAR CADA PREFERENCIA
        # ========================================================

        for indice, reg in enumerate(registros):

            try:

                plan_cuentas = reg.get("plan_cuentas")
                plan_cuentas_concilia = reg.get("plan_cuentas_concilia")
                concepto = reg.get("concepto_codigo")
                detalle_original = reg.get("detalle")
                id_conciliacion = reg.get("idConciliacion")
                importe = reg.get("importe")
                concepto_nombre = reg.get("concepto_nombre")
                pase = reg.get("pase")

                # =================================================
                # VALIDACIONES
                # =================================================

                campos_faltantes = []

                if not id_conciliacion:
                    campos_faltantes.append("idConciliacion")

                if not plan_cuentas:
                    campos_faltantes.append("plan_cuentas")

                if not plan_cuentas_concilia:
                    campos_faltantes.append("plan_cuentas_concilia")

                if not detalle_original:
                    campos_faltantes.append("detalle")

                if campos_faltantes:

                    errores.append({
                        "indice": indice,
                        "registro": reg,
                        "error": "Registro inválido",
                        "campos_faltantes": campos_faltantes
                    })

                    logging.warning(
                        f"Registro inválido [{indice}] - "
                        f"Campos faltantes: {campos_faltantes} - "
                        f"Registro: {reg}"
                    )

                    continue

                # =================================================
                # MISMO DETALLE QUE SE VA A GUARDAR
                # =================================================

                detalle = str(detalle_original)[:50]

                # =================================================
                # ALTA
                # =================================================

                if accion == 1 or accion == "1":

                    # ------------------------------------------------
                    # VERIFICAR SI YA EXISTE
                    # ------------------------------------------------

                    sql = """
                        SELECT
                            id,
                            idEmpresa,
                            plan_cuenta_concilia,
                            plan_cuentas,
                            concepto,
                            detalle,
                            estado
                        FROM SisMasterTotalesGuarda
                        WHERE idEmpresa = %s
                          AND plan_cuenta_concilia = %s
                          AND plan_cuentas = %s
                          AND detalle = %s
                        LIMIT 1
                    """

                    cursor.execute(
                        sql,
                        (
                            clientId,
                            plan_cuentas_concilia,
                            plan_cuentas,
                            detalle
                        )
                    )

                    existente = cursor.fetchone()

                    # ------------------------------------------------
                    # YA EXISTE
                    # ------------------------------------------------

                    if existente:

                        ya_existentes.append({
                            "indice": indice,
                            "pase": pase,
                            "detalle": detalle,
                            "importe": importe,
                            "plan_cuentas": plan_cuentas,
                            "plan_cuentas_concilia": plan_cuentas_concilia,
                            "id_existente": existente.get("id")
                        })

                        logging.info(
                            f"Preferencia ya existente: "
                            f"empresa={clientId}, "
                            f"plan_cuentas_concilia={plan_cuentas_concilia}, "
                            f"plan_cuentas={plan_cuentas}, "
                            f"detalle={detalle}"
                        )

                        continue

                    # ------------------------------------------------
                    # INSERTAR
                    # ------------------------------------------------

                    sql = """
                        INSERT INTO SisMasterTotalesGuarda
                        (
                            idEmpresa,
                            plan_cuenta_concilia,
                            plan_cuentas,
                            concepto,
                            detalle,
                            estado
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """

                    cursor.execute(
                        sql,
                        (
                            clientId,
                            plan_cuentas_concilia,
                            plan_cuentas,
                            concepto,
                            detalle,
                            1
                        )
                    )

                    # ------------------------------------------------
                    # VERIFICAR INSERT
                    # ------------------------------------------------

                    if cursor.rowcount != 1:

                        dbConnection.conn.rollback()

                        errores.append({
                            "indice": indice,
                            "registro": reg,
                            "error": "El INSERT no afectó ninguna fila."
                        })

                        logging.error(
                            f"INSERT sin afectar filas: {reg}"
                        )

                        continue

                    id_insertado = cursor.lastrowid

                    dbConnection.conn.commit()

                    insertadas.append({
                        "indice": indice,
                        "pase": pase,
                        "id": id_insertado,
                        "detalle": detalle,
                        "importe": importe,
                        "plan_cuentas": plan_cuentas,
                        "plan_cuentas_concilia": plan_cuentas_concilia
                    })

                    logging.info(
                        f"Preferencia insertada correctamente. "
                        f"id={id_insertado}, "
                        f"detalle={detalle}"
                    )

                # =================================================
                # BAJA
                # =================================================

                elif accion == 2 or accion == "2":

                    sql = """
                        DELETE FROM SisMasterTotalesGuarda
                        WHERE idEmpresa = %s
                          AND plan_cuenta_concilia = %s
                          AND plan_cuentas = %s
                          AND detalle = %s
                    """

                    cursor.execute(
                        sql,
                        (
                            clientId,
                            plan_cuentas_concilia,
                            plan_cuentas,
                            detalle
                        )
                    )

                    cantidad_eliminada = cursor.rowcount

                    if cantidad_eliminada == 0:

                        dbConnection.conn.rollback()

                        errores.append({
                            "indice": indice,
                            "registro": reg,
                            "error": "No se encontró la preferencia para eliminar."
                        })

                        logging.warning(
                            f"No se encontró preferencia para eliminar: {reg}"
                        )

                        continue

                    dbConnection.conn.commit()

                    eliminadas.append({
                        "indice": indice,
                        "pase": pase,
                        "detalle": detalle,
                        "plan_cuentas": plan_cuentas,
                        "plan_cuentas_concilia": plan_cuentas_concilia
                    })

                # =================================================
                # MODIFICACIÓN
                # =================================================

                elif accion == 3 or accion == "3":

                    sql = """
                        UPDATE SisMasterTotalesGuarda
                        SET
                            concepto = %s,
                            detalle = %s
                        WHERE idEmpresa = %s
                          AND plan_cuenta_concilia = %s
                          AND plan_cuentas = %s
                    """

                    cursor.execute(
                        sql,
                        (
                            concepto,
                            detalle,
                            clientId,
                            plan_cuentas_concilia,
                            plan_cuentas
                        )
                    )

                    cantidad_modificada = cursor.rowcount

                    if cantidad_modificada == 0:

                        dbConnection.conn.rollback()

                        errores.append({
                            "indice": indice,
                            "registro": reg,
                            "error": "No se encontró la preferencia para modificar."
                        })

                        logging.warning(
                            f"No se modificó ninguna preferencia: {reg}"
                        )

                        continue

                    dbConnection.conn.commit()

                    modificadas.append({
                        "indice": indice,
                        "pase": pase,
                        "detalle": detalle,
                        "plan_cuentas": plan_cuentas,
                        "plan_cuentas_concilia": plan_cuentas_concilia
                    })

                # =================================================
                # ACCIÓN INVÁLIDA
                # =================================================

                else:

                    errores.append({
                        "indice": indice,
                        "registro": reg,
                        "error": f"Acción ABM inválida: {accion}"
                    })

                    logging.warning(
                        f"Acción ABM inválida: {accion}"
                    )

            except Exception as error_registro:

                # -----------------------------------------------
                # ROLLBACK DEL REGISTRO
                # -----------------------------------------------

                try:
                    dbConnection.conn.rollback()
                except Exception:
                    pass

                logging.exception(
                    f"Error procesando preferencia [{indice}]"
                )

                errores.append({
                    "indice": indice,
                    "registro": reg,
                    "error": str(error_registro)
                })

        # ============================================================
        # RESUMEN
        # ============================================================

        total_recibidos = len(registros)
        total_insertadas = len(insertadas)
        total_existentes = len(ya_existentes)
        total_eliminadas = len(eliminadas)
        total_modificadas = len(modificadas)
        total_errores = len(errores)

        # ============================================================
        # ALTA: ALGUNAS YA EXISTÍAN
        # ============================================================

        if accion == 1 or accion == "1":

            # Todas nuevas
            if total_insertadas == total_recibidos:

                return jsonify({
                    "control": {
                        "codigo": 200,
                        "estado": "OK",
                        "mensaje": "Todas las preferencias fueron guardadas correctamente."
                    },
                    "resumen": {
                        "recibidos": total_recibidos,
                        "insertadas": total_insertadas,
                        "ya_existentes": total_existentes,
                        "errores": total_errores
                    },
                    "datos": insertadas,
                    "ya_existentes": ya_existentes,
                    "errores": errores
                }), 200

            # Algunas nuevas y algunas existentes
            elif total_insertadas > 0 and total_existentes > 0:

                return jsonify({
                    "control": {
                        "codigo": 207,
                        "estado": "Advertencia",
                        "mensaje": "Algunas preferencias fueron guardadas y otras ya existían."
                    },
                    "resumen": {
                        "recibidos": total_recibidos,
                        "insertadas": total_insertadas,
                        "ya_existentes": total_existentes,
                        "errores": total_errores
                    },
                    "datos": insertadas,
                    "ya_existentes": ya_existentes,
                    "errores": errores
                }), 207

            # Todas ya existían
            elif total_insertadas == 0 and total_existentes == total_recibidos:

                return jsonify({
                    "control": {
                        "codigo": 207,
                        "estado": "Advertencia",
                        "mensaje": "Todas las preferencias ya existían. No se realizaron nuevas inserciones."
                    },
                    "resumen": {
                        "recibidos": total_recibidos,
                        "insertadas": 0,
                        "ya_existentes": total_existentes,
                        "errores": total_errores
                    },
                    "datos": [],
                    "ya_existentes": ya_existentes,
                    "errores": errores
                }), 207

        # ============================================================
        # BAJA
        # ============================================================

        if accion == 2 or accion == "2":

            if total_errores == 0:

                return jsonify({
                    "control": {
                        "codigo": 200,
                        "estado": "OK",
                        "mensaje": "Las preferencias fueron eliminadas correctamente."
                    },
                    "resumen": {
                        "recibidos": total_recibidos,
                        "eliminadas": total_eliminadas,
                        "errores": total_errores
                    },
                    "datos": eliminadas,
                    "errores": errores
                }), 200

            return jsonify({
                "control": {
                    "codigo": 207,
                    "estado": "Advertencia",
                    "mensaje": "Algunas preferencias no pudieron eliminarse."
                },
                "resumen": {
                    "recibidos": total_recibidos,
                    "eliminadas": total_eliminadas,
                    "errores": total_errores
                },
                "datos": eliminadas,
                "errores": errores
            }), 207

        # ============================================================
        # MODIFICACIÓN
        # ============================================================

        if accion == 3 or accion == "3":

            if total_errores == 0:

                return jsonify({
                    "control": {
                        "codigo": 200,
                        "estado": "OK",
                        "mensaje": "Las preferencias fueron modificadas correctamente."
                    },
                    "resumen": {
                        "recibidos": total_recibidos,
                        "modificadas": total_modificadas,
                        "errores": total_errores
                    },
                    "datos": modificadas,
                    "errores": errores
                }), 200

            return jsonify({
                "control": {
                    "codigo": 207,
                    "estado": "Advertencia",
                    "mensaje": "Algunas preferencias no pudieron modificarse."
                },
                "resumen": {
                    "recibidos": total_recibidos,
                    "modificadas": total_modificadas,
                    "errores": total_errores
                },
                "datos": modificadas,
                "errores": errores
            }), 207

        # ============================================================
        # SI NO SE PROCESÓ NADA
        # ============================================================

        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": "No se pudo procesar ninguna preferencia."
            },
            "resumen": {
                "recibidos": total_recibidos,
                "insertadas": total_insertadas,
                "ya_existentes": total_existentes,
                "eliminadas": total_eliminadas,
                "modificadas": total_modificadas,
                "errores": total_errores
            },
            "datos": [],
            "ya_existentes": ya_existentes,
            "errores": errores
        }), 400

    except Exception as e:

        logging.exception(
            "Error general al procesar preferencias"
        )

        try:
            dbConnection.conn.rollback()
        except Exception:
            pass

        return jsonify({
            "control": {
                "codigo": 500,
                "estado": "Error",
                "mensaje": f"Error al procesar registros: {str(e)}"
            },
            "datos": [],
            "errores": [
                {
                    "error": str(e)
                }
            ]
        }), 500

    finally:

        close_connection(
            cursor,
            dbConnection.conn
        )





def getAbmPreferenciasOriginal():
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    registros = data.get('preferencias_registros', [])
    accion = data.get('abm', 1)  # 1: alta, 2: baja, 3: modificación

    if not registros:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": "No se recibieron registros de preferencias."
            }
        })

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "codigo": 401,
                "estado": "Error",
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)

        for reg in registros:
            plan_cuentas = reg.get("plan_cuentas")
            plan_cuentas_concilia = reg.get("plan_cuentas_concilia")
            concepto = reg.get("concepto_codigo")
            detalle = reg.get("detalle")
            id_conciliacion = reg.get("idConciliacion")

            if not id_conciliacion or not plan_cuentas or not detalle or not plan_cuentas_concilia:
                logging.warning(f"Registro inválido: {reg}")
                continue

            if accion == 1 or accion == "1":  # ALTA
                sql = """SELECT COUNT(*) AS existe
                           FROM SisMasterTotalesGuarda
                          WHERE idEmpresa = %s
                            AND plan_cuenta_concilia = %s
                            AND plan_cuentas = %s
                            AND detalle = %s"""
                cursor.execute(sql, (clientId, plan_cuentas_concilia, plan_cuentas, detalle))
                resultado = cursor.fetchone()
                existe = resultado["existe"] if resultado else 0

                if existe == 0:
                    deta = detalle[:50]  # 🔎 acortar detalle a 20 caracteres
                    sql = """INSERT INTO SisMasterTotalesGuarda 
                                (idEmpresa, plan_cuenta_concilia, plan_cuentas, concepto, detalle, estado)
                             VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (clientId, plan_cuentas_concilia, plan_cuentas, concepto, deta, 1))
                    dbConnection.conn.commit()

            elif accion == 2 or accion == "2":  # BAJA
                sql = """DELETE FROM SisMasterTotalesGuarda
                           WHERE idEmpresa = %s
                             AND plan_cuenta_concilia = %s
                             AND plan_cuentas = %s
                             AND detalle = %s"""
                cursor.execute(sql, (clientId, plan_cuentas_concilia, plan_cuentas, detalle))
                dbConnection.conn.commit()

            elif accion == 3 or accion == "3":  # MODIFICACIÓN
                sql = """UPDATE SisMasterTotalesGuarda
                            SET concepto = %s, detalle = %s
                          WHERE idEmpresa = %s
                            AND plan_cuenta_concilia = %s
                            AND plan_cuentas = %s"""
                cursor.execute(sql, (concepto, detalle[:20], clientId, plan_cuentas_concilia, plan_cuentas))
                dbConnection.conn.commit()

        return jsonify({
            "control": {
                "codigo": 200,
                "estado": "OK",
                "mensaje": "Operación realizada correctamente sobre los registros enviados."
            }
        })

    except Exception as e:
        logging.error(f"Error al procesar registros: {e}")
        return jsonify({
            "control": {
                "codigo": 500,
                "estado": "Error",
                "mensaje": f"Error al procesar registros: {str(e)}"
            }
        })
    finally:
        close_connection(cursor, dbConnection.conn)



@concilia_rest_bp.route('/cuentas-contables-abm', methods=['POST'])
def getAbmCuentasContables():
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    idConciliacion = data.get('id_conciliacion')
    cuentaContable  = data.get('cuenta', None)
    padronCodigo = data.get('cta_padron', None)
    print("--------------------------------------------------------------------------")
    logging.info(cuentaContable)
    print("--------------------------------------------------------------------------")
    # Convertir a diccionario
    accion = data.get('abm', 0)  # 1: alta, 2: baja, 3: actualización

    if not padronCodigo:
        padronCodigo = 0


    if not cuentaContable:
        logging.error(getHttpStatusDescription(400) + " | cuenta contable no recibida.")
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | cuenta contable no recibida.",
            }
        })


    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        })

    cursor = None
    try:

        # recorro el objeto cuenta contable

        if cuentaContable:
            tipo_cuenta = cuentaContable.get('tipo_cuenta', 1)
            descripcion = cuentaContable.get('descripcion', None)
            plan_cuentas = cuentaContable.get('plan_cuentas', None)

            id_cuenta = cuentaContable.get('id', 0)
            print(f"Tipo de Cuenta: {tipo_cuenta}")
            print(f"Descripción: {descripcion}")
            print(f"Número de Cuenta: {plan_cuentas}")
            print(f"Id Cuenta Contable: {id_cuenta}")

        else:
            print("No se encontró el objeto cuentaContable")


        if accion == 1 or  accion == "1":
            dbConnection.conn.connect()
            cursor = dbConnection.conn.cursor(dictionary=True)
            # ANTES DE INSERTAR VERIFICO SI EXISTE LA CUENTA YA CREADA
            sql = """ SELECT COUNT(*)  AS cuenta_existente 
                                        FROM PlanCuentas
                                        WHERE idEmpresa = %s 
                                          AND tipo_cuenta = %s 
                                          AND plan_cuentas = %s
                                        """
            cursor.execute(sql, (clientId, tipo_cuenta, plan_cuentas))
            resultado = cursor.fetchone()
            existe = resultado["cuenta_existente"] if resultado else 0
            if  existe > 0:
                logging.error("La cuenta contable ya existe, no puede darla de alta")
                return jsonify({
                    "control": {
                        "control": "ERROR",
                        "codigo": "400",
                        "mensaje": "La cuenta contable "+str(plan_cuentas)+" que intenta crear ya existe."
                    }
                })
            else:
               sql = """INSERT INTO PlanCuentas (idEmpresa, tipo_cuenta,  plan_cuentas, padron_codigo, descripcion, orden)
                         VALUES (%s, %s, %s, %s,  %s, %s);"""
               cursor.execute(sql, (clientId, tipo_cuenta, plan_cuentas, padronCodigo, descripcion, 1) )
               dbConnection.conn.commit()
               if cursor.rowcount > 0:
                    logging.info("Registro insertado correctamente.")
                    return jsonify({
                        "control": {
                            "control": "OK",
                            "codigo": "200",
                            "mensaje": "Cuenta contable creada correctamente."
                        }

                    })
               else:
                    logging.error("Error al insertar el registro.")
                    return jsonify({
                        "control": {
                            "control": "ERROR",
                            "codigo": "500",
                            "mensaje": "Error al crear la cuenta contable requerida, inténte nuevamente más tarde."
                        }
                    })
        elif accion == 2 or accion == "2":
            logging.info("Borro una cuenta contable.")
            dbConnection.conn.connect()
            cursor = dbConnection.conn.cursor(dictionary=True)
            id_cuenta = cuentaContable.get('id', 0)

            sql = """ SELECT COUNT(*) AS cuenta_existente FROM PlanCuentas  WHERE idEmpresa = %s AND id = %s"""
            cursor.execute(sql, (clientId, id_cuenta))
            resultado = cursor.fetchone()
            existe = resultado["cuenta_existente"] if resultado else 0

            if existe > 0:

                sql = """DELETE FROM PlanCuentas WHERE idEmpresa = %s AND id = %s"""
                cursor.execute(sql, (clientId, id_cuenta))
                dbConnection.conn.commit()



                sql_verify = """SELECT COUNT(*) as cuenta_existente FROM PlanCuentas WHERE idEmpresa = %s AND id = %s"""
                cursor.execute(sql_verify, (clientId, id_cuenta))
                resultado = cursor.fetchone()
                eliminado = resultado["cuenta_existente"] if resultado else 0

                if eliminado == 0:
                    sql = """DELETE FROM SisMasterTotalesGuarda WHERE idEmpresa = %s AND plan_cuentas = %s"""
                    cursor.execute(sql, (clientId, plan_cuentas))
                    dbConnection.conn.commit()
                    logging.info("La cuenta contable "+str(plan_cuentas)+" se elimino con éxito.")

                    return jsonify({
                        "control": {
                            "control": "OK",
                            "codigo": "200",
                            "mensaje": "La cuenta contable se elimino con éxito."
                        }
                    })
                else:
                    return jsonify({
                        "control": {
                            "control": "ERROR",
                            "codigo": "400",
                            "mensaje": "Ocurrió un problema al eliminar la cuenta contable, aún existe."
                        }
                    })
                 # Verificar si el registro sigue existiendo


            else:

                return jsonify({
                    "control": {
                        "control": "ERROR",
                        "codigo": "400",
                        "mensaje": "La cuenta contable "+str(plan_cuentas)+" que intenta eliminar no existe."
                    }
                })
        elif accion == 3 or accion == "3":
            logging.info("Actualizo una cuenta contable.")
            dbConnection.conn.connect()
            cursor = dbConnection.conn.cursor(dictionary=True)
            id_cuenta = cuentaContable.get('id', 0)
            sql = """ SELECT COUNT(*) AS cuenta_existente FROM PlanCuentas  WHERE idEmpresa = %s AND id = %s"""
            cursor.execute(sql, (clientId, id_cuenta))
            resultado = cursor.fetchone()
            existe = resultado["cuenta_existente"] if resultado else 0

            if existe > 0 :
                sql = """UPDATE PlanCuentas SET descripcion = %s, padron_codigo = %s, plan_cuentas = %s WHERE idEmpresa = %s  and id = %s and estado = 1"""
                cursor.execute(sql, (descripcion,  padronCodigo, plan_cuentas, clientId, id_cuenta))
                dbConnection.conn.commit()
                if cursor.rowcount > 0:
                    logging.info("Cuenta contable actualizada correctamente.")
                    return jsonify({
                        "control": {
                            "control": "OK",
                            "codigo": "200",
                            "mensaje": "Cuenta contable actualizada correctamente."
                        }
                    })
                else:
                    logging.error("Ocurrió un problema al actualizar la cuenta contable.")
                    return jsonify({
                        "control": {
                            "control": "ERROR",
                            "codigo": "400",
                            "mensaje": "Ocurrió un problema al actualizar la cuenta contable."
                        }
                    })

        else:
            logging.error("ABM no válido, debe ser 1 (alta), 2 (baja) o 3 (actualización).")
            return jsonify({
                "control": {
                    "control": "ERROR",
                    "codigo": "400" ,
                    "mensaje": "ABM no válido, debe ser 1 (alta), 2 (baja) o 3 (actualización).",
                },
                "datos":[]
            })
    except Exception as e:
        logging.error(f"Error al ejecutar el SELECT: {e}")
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": "500",
                "mensaje": f"Error intentar procesar la cuenta contable, intente nuevamente más tarde, o póngase en contacto con el administrador del sistema: {str(e)}"
            },
            "datos": []
        })
    finally:
        close_connection(cursor, dbConnection.conn)




@concilia_rest_bp.route('/traer-parametros', methods=['POST'])
def getParametros():
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    idConcilia = data.get('id_concilia')
    grupo = data.get('grupo', None)
    codigo = data.get('codigo', None)
    nombreParametro = data.get('nombre_parametro', None)

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)
        if grupo is None or grupo == "":
            print("SELECT POR GRUPO")
            sql = """
            SELECT * FROM Parametros
            WHERE idEmpresa = %s AND grupo = %s ORDER BY orden ASC
            """
            cursor.execute(sql, (clientId, grupo))
        elif grupo and nombreParametro:
            print("SELECT POR GRUPO, CODIGO Y NOMBRE PARAMETRO")
            sql = """
            SELECT * FROM Parametros
            WHERE idEmpresa = %s AND grupo = %s and nombreParametro = %s ORDER BY orden ASC
            """
            cursor.execute(sql, (clientId, grupo, nombreParametro))
        resultados = cursor.fetchall()

        parametros = [
            {
                "idParametro": row["idParametro"],
                "grupo": row["grupo"],
                "codigo": row["codigo"],
                "nombreParametro": row["nombreParametro"],
                "valor": row["valor"],

            }
            for row in resultados
        ]

        mensaje = f"Se han encontrado {len(parametros)}." if parametros else "No se encontraron parametros."
        logging.info(mensaje)
        return jsonify({
            "control": {
                "control": "OK",
                "codigo": "200",
                "mensaje": mensaje,
            },
            "datos": parametros
        })
    except Exception as e:
        logging.error(f"Error al ejecutar el SELECT: {e}")
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": "500",
                "mensaje": f"Error al obtener parametros: {str(e)}"
            },
            "datos": []
        })
    finally:
        close_connection(cursor, dbConnection.conn)



@concilia_rest_bp.route('/confirmar-conciliacion-final', methods=['POST'])
def setConfirmarConciliacionFinal():
    logging.info("---------------------> Entrando a setConfirmarConciliacionFinal")
    data = request.get_json()
    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos.",
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    idConciliacion = data.get('id_conciliacion')
    movimientosConciliados  = data.get('movimientos_conciliados')

    if not movimientosConciliados:
        logging.error(getHttpStatusDescription(400) + " | No se recibieron movimientos para conciliar.")
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | No se recibieron movimientos para conciliar.",
            }
        })


    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": []
        })

    cursor = None
    try:

        # recorro el objeto cuenta contable

        if not movimientosConciliados:
            print("No se recibieron movimientos para conciliar")
            return jsonify({
                "control": {
                    "control": "ERROR",
                    "codigo": 400,
                    "mensaje": "No se recibieron movimientos para conciliar"
                },

            })

        else:
            for row in movimientosConciliados:
                logging.info(f"Fila recibida: {row}")
            dbConnection.conn.connect()
            cursor = dbConnection.conn.cursor(dictionary=True)
            # HAGO EL  UPDASTE DE CADA MOVMIENTO CONCILIADO POR idMaster
            print("- Movimientos Conciliados -------------------------------------------------------------------------")
            print(movimientosConciliados)
            print("---------------------------------------------------------------------------------------------------")
            for row in movimientosConciliados:
                id_master = row["id_master"]
                asiento_concilia = row["asiento_concilia"]
                sql = """
                    UPDATE SisMaster
                    SET procesado_sn = 'S'
                    WHERE idMaster = %s and m_asiento_concilia = %s  and estado = 1 and idUsuario = %s
                """
                cursor.execute(sql, (id_master, asiento_concilia, userId))
                dbConnection.conn.commit()

            return jsonify({
                "control": {
                    "control": "OK",
                    "codigo": "200",
                    "mensaje": "Movimientos conciliados actualizados correctamente."
                }
            })
            cursor.close()



    except Exception as e:
        logging.error(f"Error al ejecutar el SELECT: {e}")
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": "500",
                "mensaje": f"Error intentar procesar la cuenta contable, intente nuevamente más tarde, o póngase en contacto con el administrador del sistema: {str(e)}"
            },
            "datos": []
        })
    finally:
        close_connection(cursor, dbConnection.conn)






@concilia_rest_bp.route('/traer-no-conciliados', methods=['POST'])
def getNoConciliados():
    data = request.get_json()

    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400) + " | datos o parámetros no recibidos."
            },
            "datos": {
                "empresa_no_conciliados": [],
                "banco_no_conciliados": []
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    idConciliacion = data.get('id_conciliacion')

    if not token or not userId or not clientId or not idConciliacion:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": "Faltan parámetros obligatorios."
            },
            "datos": {
                "empresa_no_conciliados": [],
                "banco_no_conciliados": []
            }
        })

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            },
            "datos": {
                "empresa_no_conciliados": [],
                "banco_no_conciliados": []
            }
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)

        sql_empresa = """
            SELECT * FROM SisMaster
            WHERE idUsuario = %s
              AND idEmpresa = %s
              AND idConcilia = %s
              AND procesado_sn = 'N'  AND importe != 0
              AND estado in(4) order by saldo asc
        """

        cursor.execute(sql_empresa, (userId, clientId, idConciliacion))
        resultados_empresa = cursor.fetchall()
        logging.info(":::::::::: traer-no-conciliados' ----> "+str(clientId)+" , " +str(idConciliacion))
        empresa_no_conciliados = [
            {
                "id_master": row["idMaster"],
                "id_cab_concilia": row["idCabConcilia"],
                "m_ingreso": row["m_ingreso"],
                "asiento_concilia": row["m_asiento_concilia"],
                "id_concilia" : row["idConcilia"],
                "pase": row["m_pase"],
                "concepto": row["concepto"],
                # si nro_comp_asoc = 0, mostrar nro_comp
                "comprobante": (
                    row["nro_comp_asoc"] if row["nro_comp_asoc"] != 0
                    else (row["nro_comp"] if row["nro_comp"] != 0 else row["cuit"])
                ),
                #"comprobante": row["nro_comp"],
                "comprobante_asoc": row["nro_comp_asoc"],
                "detalle": row["detalle"],
                "plan_cuenta": row["plan_cuentas"],
                "padron_codigo" : row["padron_codigo"],
                "asiento": row["m_asiento"],
                "saldo": row["saldo"],
                "codigo": row["codigo"],
                "cuit": row["cuit"],
                "importe": row["importe"]
            }
            for row in resultados_empresa
        ]

        sql_banco = """
            SELECT * FROM SisMaster
            WHERE idUsuario = %s
              AND idEmpresa = %s
              AND idConcilia = %s
              AND procesado_sn = 'N'  AND importe != 0
              AND estado in (5) order by saldo asc
        """
        cursor.execute(sql_banco, (userId, clientId, idConciliacion))
        resultados_banco = cursor.fetchall()

        banco_no_conciliados = [
            {
                "id_master": row["idMaster"],
                "id_cab_concilia": row["idCabConcilia"],
                "m_ingreso": row["m_ingreso"],
                "asiento_concilia": row["m_asiento_concilia"],
                "pase": row["m_pase"],
                "concepto": row["concepto"],
                "id_concilia": row["idConcilia"],
                "comprobante": row["nro_comp"],
                "comprobante_asoc": row["nro_comp_asoc"],
                "detalle": row["detalle"],
                "plan_cuenta": row["plan_cuentas"],

                "padron_codigo": row["padron_codigo"],
                "asiento": row["m_asiento"],
                "saldo": row["saldo"],
                "codigo": row["codigo"],
                "cuit": row["cuit"],
                "importe": row["importe"]
            }
            for row in resultados_banco
        ]

        return jsonify({
            "control": {
                "control": "OK",
                "codigo": 200,
                "mensaje": "Movimientos no conciliados obtenidos correctamente."
            },
            "datos": {
                "empresa_no_conciliados": empresa_no_conciliados,
                "banco_no_conciliados": banco_no_conciliados
            }
        })

    except Exception as e:
        logging.error(f"Error al obtener no conciliados: {e}")
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 500,
                "mensaje": f"Error al obtener movimientos no conciliados: {str(e)}"
            },
            "datos": {
                "empresa_no_conciliados": [],
                "banco_no_conciliados": []
            }
        })
    finally:
        close_connection(cursor, dbConnection.conn)





@concilia_rest_bp.route('/marcar-conciliacion', methods=['POST'])
def marcarConciliacion():
    data = request.get_json()

    if not data:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": "datos o parámetros no recibidos."
            }
        })

    token = data.get('token')
    userId = data.get('id_usuario')
    clientId = data.get('id_empresa')
    idConciliacion = data.get('id_conciliacion')
    movimiento = data.get('movimiento', {})
    estado = data.get('estado')
    logging.info(jsonify(movimiento))
    logging.info(f"Estado recibido: {estado}")
    logging.info("idConciliacion: "+str(idConciliacion)+", Usuario: "+str(userId))
    if not token or not userId or not clientId or not idConciliacion or not movimiento:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": "Faltan parámetros obligatorios."
            }
        })

    if not checkValidityTokenByToken(token, userId):
        return jsonify({
            "control": {
                "control": "ERROR",
                "codigo": 401,
                "mensaje": "Token inválido o expirado, loguearse nuevamente."
            }
        })

    id_master = movimiento.get('id_master')
    id_master_entidad = movimiento.get('id_master_entidad')

    if not id_master:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": "No se recibió id_master."
            }
        })

    # Mapear estados según especificación:
    # Empresa: conciliado -> 1, no_conciliado/desmarcado -> 4
    # Banco/Entidad: conciliado -> 5, no_conciliado/desmarcado -> 6
    if estado == "conciliado":
        estado_empresa = 1
        estado_entidad = 6
    elif estado in ["no_conciliado", "desmarcado"]:
        estado_empresa = 4
        estado_entidad = 5
    else:
        return jsonify({
            "control": {
                "codigo": 400,
                "estado": "Error",
                "mensaje": "Estado inválido. Use 'conciliado', 'no_conciliado' o 'desmarcado'."
            }
        })

    cursor = None
    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)

        sql = """UPDATE SisMaster
                 SET estado = %s,
                     procesado_sn = %s
                 WHERE idMaster = %s
                   AND idUsuario = %s
                   AND idEmpresa = %s
                   AND idConcilia = %s
              """

        # Actualizar registro de la empresa (id_master)
        cursor.execute(sql, (estado_empresa, 'N', id_master, userId, clientId, idConciliacion))
        dbConnection.conn.commit()

        if cursor.rowcount <= 0:
            return jsonify({
                "control": {
                    "codigo": 404,
                    "estado": "Error",
                    "mensaje": f"No se encontró el movimiento de empresa para actualizar (id_master={id_master})."
                }
            })

        # Si se proporciona id_master_entidad, actualizar el registro correspondiente
        db_entidad_result = {"updated": False}
        if id_master_entidad:
            cursor.execute(sql, (estado_entidad, 'N', id_master_entidad, userId, clientId, idConciliacion))
            dbConnection.conn.commit()
            db_entidad_result["updated"] = cursor.rowcount > 0

        return jsonify({
            "control": {
                "codigo": 200,
                "estado": "OK",
                "mensaje": f"Movimientos marcados correctamente. Empresa actualizado a estado {estado_empresa}."
            },
            "detalle": {
                "empresa_id_master": id_master,
                "entidad_id_master": id_master_entidad,
                "entidad_actualizada": db_entidad_result.get("updated", False)
            }
        })

    except Exception as e:
        logging.error(f"Error al actualizar conciliación: {e}")
        return jsonify({
            "control": {
                "codigo": 500,
                "estado": "Error",
                "mensaje": f"Error al actualizar conciliación: {str(e)}"
            }
        })
    finally:
        close_connection(cursor, dbConnection.conn)


# Ruta: dummy
@concilia_rest_bp.route('/dummy', methods=['GET'])
def dummy():
    data = {
        "code": "1",
        "version": "1.0",
        "status": 200,
        "description": "Conciliación.",
        "name": "Conciliación Bancaria",
        "message": "Conciliación Bancaria, servicio de conciliación funciona correctamente.",
        "functions": ["login", "recoverPassword", "logout"]
    }
    return jsonify(data)