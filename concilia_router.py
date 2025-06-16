import hashlib
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
        WHERE idUsuario = %s AND idEmpresa = %s AND procesado_sn = 'N' AND estado = 1 AND idConcilia = %s
        """
        cursor.execute(sql, (userId, clientId, id_conciliacion))
        resultados = cursor.fetchall()

        movimientos = [
            {
                "idMaster": row["idMaster"],
                "m_ingreso": row["m_ingreso"],
                "asiento_concilia": row["m_asiento_concilia"],
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

    print(":::::::::::::::::::: getDiferenciasEntidadEmpresa")
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
        SELECT * FROM SisMasterEntidad
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

        sql = """
        SELECT * FROM SisMasterTotales
        WHERE idUsuario = %s AND idEmpresa = %s AND procesado_sn = 'N' AND estado = 1 AND idConcilia = %s
        """
        cursor.execute(sql, (userId, clientId, id_conciliacion))
        resultados = cursor.fetchall()

        movimientos_tot = [
            {
                "idMaster": row["idMaster"],
                "m_ingreso": row["m_ingreso"],
                "asiento_concilia": row["m_asiento_concilia"],
                "concepto": row["concepto"],
                "plan_cuenta": row["plan_cuentas"],
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

                sql = """ SELECT PlanCuentas.id, PlanCuentas.tipo_cuenta, PlanCuentasTipos.nombre as tipo_cuenta_nombre, PlanCuentas.plan_cuentas, PlanCuentas.descripcion, PlanCuentas.orden 
                    FROM PlanCuentas, PlanCuentasTipos WHERE idEmpresa = %s AND PlanCuentas.estado = 1
                    and PlanCuentas.tipo_cuenta = PlanCuentasTipos.idTipo order by PlanCuentasTipos.idTipo, PlanCuentas.id asc """
                cursor.execute(sql, (clientId,))
            else:

                sql = """ SELECT PlanCuentas.id, PlanCuentas.tipo_cuenta, PlanCuentasTipos.nombre as tipo_cuenta_nombre, PlanCuentas.plan_cuentas, PlanCuentas.descripcion, PlanCuentas.orden 
                                    FROM PlanCuentas, PlanCuentasTipos WHERE idEmpresa = %s AND PlanCuentas.estado = 1 and PlanCuentas.id = %s
                                    and PlanCuentas.tipo_cuenta = PlanCuentasTipos.idTipo order by PlanCuentasTipos.idTipo, PlanCuentas.id asc """
                cursor.execute(sql, (clientId, id_cuenta,))
        else:
            if id_cuenta == 0 or id_cuenta is None:
                sql = """
                SELECT PlanCuentas.id, PlanCuentas.tipo_cuenta, PlanCuentasTipos.nombre as tipo_cuenta_nombre, PlanCuentas.plan_cuentas, PlanCuentas.descripcion, PlanCuentas.orden 
    FROM PlanCuentas, PlanCuentasTipos WHERE idEmpresa = %s AND PlanCuentas.estado = 1  and  tipo_cuenta = %s
    and PlanCuentas.tipo_cuenta = PlanCuentasTipos.idTipo  ORDER BY orden ASC
                """
                cursor.execute(sql, (clientId, id_tipo))
            else:
                sql = """SELECT PlanCuentas.id, PlanCuentas.tipo_cuenta, PlanCuentasTipos.nombre as tipo_cuenta_nombre, PlanCuentas.plan_cuentas, PlanCuentas.descripcion, PlanCuentas.orden 
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
    print("--------------------------------------------------------------------------")
    logging.info(cuentaContable)
    print("--------------------------------------------------------------------------")
    # Convertir a diccionario
    accion = data.get('abm', 0)  # 1: alta, 2: baja, 3: actualización




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
               sql = """INSERT INTO PlanCuentas (idEmpresa, tipo_cuenta,  plan_cuentas, descripcion, orden)
                         VALUES (%s, %s, %s, %s,  %s);"""
               cursor.execute(sql, (clientId, tipo_cuenta, plan_cuentas, descripcion, 1) )
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
                sql = """UPDATE PlanCuentas SET descripcion = %s, plan_cuentas = %s WHERE idEmpresa = %s  and id = %s and estado = 1"""
                cursor.execute(sql, (descripcion,  plan_cuentas, clientId, id_cuenta))
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