import hashlib

from flask import Blueprint, request, jsonify, Flask

auth_bp = Blueprint('/auth', __name__)
app = Flask(__name__)
app.config['DEBUG'] = True
import logging

import jwt
from datetime import datetime, timedelta
#import datetime
import json

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


@auth_bp.route('/login', methods=['POST'])
def login():
    print(":: LOGIN :::")
    try:
        # Obtener datos del JSON recibido
        data = request.get_json()
        #logging.info("Datos recibidos: %s", data)
        if not data:
            control = {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400)+" | datos o parametros no recibidos.",
            }
            return jsonify({"control": control})


        # Extraer parámetros
        username = data.get('username')
        password = data.get('password')
        clientId = data.get('clientId')




        # Validar parámetros
        if username is None or password is None or clientId is None :
            control = {
                "codigo": 400,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(400),
            }
            return jsonify({"control": control})


        # Conectar a la base de datos
        try:
            dbConnection.conn.connect()
            cursor = dbConnection.conn.cursor()


            # Construir consulta según loginType
            """if loginType == 1:  # Login por usuario
                sql = ("SELECT idUsuarios, idGrupo, nombre, apellido, clave,  mail, "
                       "telefono, observaciones FROM Usuarios "
                       "WHERE estado = 1 AND usuario = %s AND idEmpresa = %s")
                cursor.execute(sql, (username, clientId))
            elif loginType == 2:  # Login por email
                sql = ("SELECT idUsuarios, idGrupo, nombre, apellido, clave,  mail, "
                       "telefono, observaciones FROM Usuarios "
                       "WHERE estado = 1 AND mail = %s AND idEmpresa = %s")
                cursor.execute(sql, (usernameMail, clientId))
            else:
                control = {
                    "codigo": 400,
                    "estado": "Error",
                    "mensaje": getHttpStatusDescription(400),
                }
                return jsonify({"control": control})

            # Recuperar usuario"""
            sql = ("SELECT idUsuarios, idGrupo, nombre, apellido, clave, mail, "
                   "telefono, observaciones FROM Usuarios "
                   "WHERE estado = 1 AND (usuario = %s OR mail = %s) AND idEmpresa = %s")
            cursor.execute(sql, (username, username, clientId))
            user = cursor.fetchone()

        finally:
            # Asegurar desconexión de la base de datos
            dbConnection.conn.disconnect()

        if user:
            userId = user[0]
            storePasswordHash = user[4]
            hashed_password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
            if storePasswordHash == hashed_password_md5:
                if not checkValidityToken(userId):
                    # Generar nuevo token
                    dateEndT = datetime.utcnow() + timedelta(hours=6)
                    dateStart = datetime.utcnow() + timedelta()
                    token = jwt.encode(
                        {'idUsuarios': userId, 'exp': dateEndT},
                        SECRET_KEY,
                        algorithm='HS256'
                    )
                    if saveTokenAcces(user, token):
                        token_info = {"estado": "Ok", "codigo" : 200, "mensaje": getHttpStatusDescription(200), "token": token, "tokenInicio" : dateStart ,"tokenExpira": dateEndT}
                    else:
                        return jsonify({"estado": "Error", "codigo": 406, "mensaje": getHttpStatusDescription(406)})

                else:


                    token_info = {"estado": "Ok","codigo" : 200, "mensaje": getHttpStatusDescription(200), "token": checkValidityToken(userId)}

                return getUserInfo(clientId, userId, token_info)

            else:
                control = {
                    "codigo": 402,
                    "estado": "Error",
                    "mensaje": getHttpStatusDescription(402),
                }
                return jsonify({"control": control})
        else:
            control = {
                "codigo": 401,
                "estado": "Error",
                "mensaje": getHttpStatusDescription(401),
            }
            return jsonify({"control": control})

    except Exception as e:
        # Manejo de errores 132.14.160.218
        logging.info("Error en el login:", str(e))
        control = {
            "codigo": 500,
            "estado": "Error",
            "mensaje": getHttpStatusDescription(500)+" "+str(e),
        }
        return jsonify({"control": control})




def getUserInfo(clientId, userId, token):

    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor()

        sql = ("SELECT idUsuarios, idGrupo, usuario, nombre, apellido, clave,  mail, marca_cambio,"
               "telefono, observaciones FROM Usuarios "
               "WHERE estado = 1 AND idUsuarios = %s AND idEmpresa = %s")

        cursor.execute(sql, (userId, clientId))
        user = cursor.fetchone()

        if not user:
            # Si no se encuentra el usuario
            dbConnection.conn.close()
            dbConnection.conn.disconnect()
            logging.error("Usuario no encontrado")
            return jsonify({"message": "Usuario no encontrado", "Error": 404}), 404

        if user:
            # Grupos
            sql = ("SELECT idGrupo, descripcion, observaciones, tipoGrupo FROM UsuariosGrupos where idGrupo = %s and estado = 1")
            cursor.execute(sql, (user[1],))
            grupos = cursor.fetchone()
            if not grupos:
                grupos = (None, None, None, None)  # Valores predeterminados si no hay grupos

            sql = "SELECT idPermiso, idGrupo, menu, alta, baja, modificacion FROM GruposPermisos WHERE idGrupo = "+str(user[1])+" AND estado = 1"
            cursor.execute(sql)
            gruposPermisos = cursor.fetchall()

            # Si la consulta no devuelve resultados, establecer valores predeterminados
            if not gruposPermisos:
                gruposPermisos = [(0, 0, 0, 0, 0, 0)]  # Lista con tupla predeterminada
            # Crear una lista para almacenar permisos procesados
            listaGruposPermisos = []

            # Iterar sobre los permisos obtenidos
            for item in gruposPermisos:
                listaGruposPermisos.append({
                    "idPermiso": item[0],
                    "idGrupo": item[1],
                    "menu": item[2],
                    "alta": item[3],
                    "baja": item[4],
                    "modificacion": item[5]
                })





            # Cliente
            sql = "select idEmpresa, prefijo, nombre, descripcion, domicilio, cuit, clientePropio from Empresas where idEmpresa = %s and estado = 1"
            cursor.execute(sql, (clientId,))
            cli = cursor.fetchone()
            if not cli:
                cli = (None, None, None, None, None, None, None)  # Valores predeterminados



            # Templates
            sql = "select id_template, nombre, descripcion from Templates where estado = 1 and idEmpresa = %s"
            cursor.execute(sql, (clientId,))
            templates = cursor.fetchall()
            # Lista para almacenar los templates con sus configuraciones
            templates_config = []

            # Iterar sobre cada template
            for template in templates:
                template_id, nombre, descripcion = template

                # Obtener la configuración de cada template
                sql_config = "SELECT id, codigo, clase, elemento, propiedad, valor FROM TemplatesConfig WHERE id_template = %s AND estado = 1"
                cursor.execute(sql_config, (template_id,))
                propiedades = cursor.fetchall()

                # Construir el objeto del template con sus configuraciones
                template_obj = {
                    "id_template": template_id,
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "estilos": [{
                        "id_config" : config[0],
                        "codigo": config[1],
                        "clase": config[2],
                        "elemento": config[3],
                        "propiedad": config[4],
                        "valor": config[5]} for config in propiedades]
                }

                # Agregar el template con configuraciones a la lista
                templates_config.append(template_obj)

            # Accesos
            userAccess = getAccesByGrupo(clientId, grupos[0], user[0])




            if not userAccess:
                userAccess = []

            # Construir respuesta
            gruposPermisos = listaGruposPermisos
            grupos = {
                "id_grupo": grupos[0],
                "descripcion": grupos[1],
                "observaciones": grupos[2],
                "tipoGrupo": grupos[3],
                "permisos": gruposPermisos,

            }


            gruposInfo={
                "grupo": grupos,
            }

            company = {
                "id": cli[0],
                "prefijo": cli[1],
                "nombre": cli[2],
                "descripcion": cli[3],
                "domicilio": cli[4],
                "cuit": cli[5],
                "cliente_propio": cli[6],
                "dominio" : "",
                "email": "",
                "cliHash": "",
                "templates":template_obj


            }





            userInfo = {
                "id": user[0],
                "usuario": user[2],
                "nombre_apellido": user[3]+" "+user[4],
                "email": user[6],
                "marca_cambio": user[7],
                "grupos": gruposInfo,
                "menu": userAccess,


            }

            finalInfo = {
                "control" : token,
                "usuario": userInfo,
                "empresa": company,
                "token": token["token"]



            }

            # Cierra conexión antes de devolver
            dbConnection.conn.close()
            dbConnection.conn.disconnect()

            obj = utils.convertDateTimeToStr(finalInfo)
            # Convertir a JSON
            print(jsonify(obj))
            return  jsonify(obj), 200
        else:
            # Si no se encuentra el usuario
            dbConnection.conn.close()
            dbConnection.conn.disconnect()
            return jsonify({"message": "Usuario no encontrado", "Error": 404}), 404

    except Exception as e:
        # Manejar cualquier excepción
        try:
            dbConnection.conn.close()
            dbConnection.conn.disconnect()
        except Exception:
            pass  # Ignorar errores durante la desconexión
        print("Error al obtener información del usuario:", e)
        return jsonify({"message": "Error inesperado", "details": str(e)}), 500

def getAccesByGrupo(clientId, groupId, userId):
    print(":: TRAER ACCESOS :::")
    try:
        import mysql.connector
        import json

        # Establecer la conexión a la base de datos
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor(dictionary=True)

        sql = ("select UsuariosMenu.idMenu as id, UsuariosMenu.nombre, UsuariosMenu.idPadre, UsuariosMenu.orden, UsuariosMenu.icono, UsuariosMenu.nombreForm, UsuariosMenuConfig.idMenu from UsuariosMenu, UsuariosMenuConfig where UsuariosMenuConfig.idMenu = UsuariosMenu.idMenu and UsuariosMenu.enUso = 1 and UsuariosMenuConfig.idGrupo = %s and UsuariosMenuConfig.estado= 1 ")

        cursor.execute(sql, (groupId, ))
        menu = cursor.fetchall()
        cursor.close()
        dbConnection.conn.close()
        elementos = {item["id"]: item for item in menu}

        for item in elementos.values():
            item["hijos"] = []

            # Organizar los elementos en una estructura jerárquica
        menus = []
        for item in elementos.values():
            if item["idPadre"] == 0 or item["idPadre"] == "/":  # Manejar raíz o casos especiales
                menus.append(item)
            elif item["idPadre"] in elementos:
                elementos[item["idPadre"]]["hijos"].append(item)
            else:
                logging.warning(
                    f"Advertencia: El id_padre {item['idPadre']} no existe en los elementos. Elemento: {item}"
                )
                # Opcional: Agregar a un grupo especial o manejarlo de otra forma
                menus.append(item)
        # Convertir a JSON


        menu_json = menus

        return menu_json




    except Exception as e:
          # Manejar cualquier excepción que ocurra

          print("Error al obtener los accesos y permisos:", e)
          return None

def checkPassword(hashedPassword, userPasswordTemp):
    # Compara la contraseña proporcionada con el hash almacenado
    hashed_password_md5 = hashlib.md5(userPasswordTemp.encode('utf-8')).hexdigest()
    if hashedPassword == hashed_password_md5:
        return True
    else:
        return False

def checkValidityToken(idUser):


    try:
        nowT = datetime.now()
        now = nowT.strftime('%Y-%m-%d %H:%M:%S')

        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor()
        sql = '''select idAcceso, tokenTipo, token, fechaDesde, fechaHasta from Accesos where  idUsuario = %s and fechaHasta >= %s '''
        cursor.execute(sql, (idUser, now))

        valid = cursor.fetchall()
        if valid:
            for tok in valid:
                tokenInfo = {
                    "id" : tok[0],
                    "tipo" : tok[1],
                    "token":  tok[2],
                    "token_inicio": tok[3],
                    "token_expira": tok[4]
                }
                return tokenInfo
            else:
                return False
        else:
            return False
        if cursor:
            cursor.close()
        if dbConnection.conn:
            dbConnection.conn.close()
    except Exception as e:
        print("Error al ejecutar la consulta:", e)
        return False



def checkValidityTokenByToken(token, idUser):
    logging.info("VALIDO TOKEN:::::: "+str(token))

    try:
        nowT = datetime.now()
        now = nowT.strftime('%Y-%m-%d %H:%M:%S')

        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor()
        sql = '''select idAcceso, tokenTipo, token, fechaDesde, fechaHasta from Accesos where  token = %s and idUsuario = %s and fechaHasta >= %s '''
        cursor.execute(sql, (token, idUser, now))

        valid = cursor.fetchall()
        if valid:
            for tok in valid:
                tokenInfo = {
                    "id" : tok[0],
                    "tipo" : tok[1],
                    "token":  tok[2],
                    "token_inicio": tok[3],
                    "token_expira": tok[4]
                }

                return True
            else:
                return False
        else:
            return False
        print(tokenInfo)
        if cursor:
            cursor.close()
        if dbConnection.conn:
            dbConnection.conn.close()
    except Exception as e:
        print("Error al ejecutar la consulta:", e)
        return False


def saveTokenAcces(user,   token):
    try:
        if user:
            user_id = user[0]
            stored_hashed_password = user[1]
            decodeToken = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            expirationTime = datetime.fromtimestamp(decodeToken['exp']).strftime('%Y-%m-%d %H:%M:%S')
            startDate = datetime.now()
            startDateTime = startDate.strftime('%Y-%m-%d %H:%M:%S')

            userId =  user[1]
            dbConnection.conn.connect()
            cursor = dbConnection.conn.cursor()
            sql = "INSERT INTO Accesos (idUsuario, token, fechaDesde, fechaHasta, fechaCreacion, tokenTipo) VALUES (%s, %s, %s,%s,%s,%s)"
            logging.info(user_id, token,  startDateTime, expirationTime, startDateTime, "HASH256")
            cursor.execute(sql, (user_id, token,  startDateTime, expirationTime, startDateTime, "HASH256"))
            dbConnection.conn.commit()
            # Verificación del registro insertado
            verify_sql = "SELECT * FROM Accesos WHERE idUsuario = %s AND token = %s"
            cursor.execute(verify_sql, (user_id, token))
            result = cursor.fetchone()

            if result:
                logging.info("Registro insertado correctamente: %s", result)
                return True
            else:
                return False
                logging.warning("No se encontró el registro insertado.")



    except jwt.ExpiredSignatureError:
        return None  # El token ha expirado
    except jwt.InvalidTokenError:
        return None  # El token no es válido




@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Aquí va la lógica de cierre de sesión
    return jsonify({"message": "Logout successful"})

@auth_bp.route('/recoverPassword', methods=['POST'])
def recover_password():
    data = request.get_json()
    email = data.get('email')

    # Aquí va la lógica de recuperación de contraseña
    return jsonify({"message": "Password recovery email sent", "email": email})

@auth_bp.route('/dummy', methods=['GET'])
def dummy():
    import json
    data = {
        "code": "1",
        "version": "1.0",
        "status": 200,
        "description": "Servicio de autentificación de Conciliacion",
        "name": "Conciliaciones",
        "message": "Conciliaciones, servicio de autentificacion funciona correctamente.",
        "functions": ["login", "recoverPassword", "logout"]
    }
    json_output = json.dumps(data, indent=4)
    logging.info(json_output)
    return json_output



