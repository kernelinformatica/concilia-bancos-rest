import logging

import bcrypt
import jwt
from datetime import datetime, timedelta
#import datetime
import json
import utils
from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS
import utils as utilities

from conn.AppConnection import AppConnection
from utils.authHttpCodes import getHttpStatusDescription
auth_bp = Blueprint('auth', __name__)
app = Flask(__name__)
app.config['DEBUG'] = True

CORS(app)
dbConnection = AppConnection()
SECRET_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF9vcGVyYWRvciI6MSwiZXhwIjoxNzM5MTI2MTM4fQ.Hg_r0q11mI4Ub7RVwCozuHF_bXpAvnEAEC4sSGQot7M'

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        # Obtener datos del JSON recibido
        data = request.get_json()
        if not data:
            return jsonify({"codigo": "ERROR", "descripcion": "Datos no recibidos"}), 400

        # Extraer parámetros
        username = data.get('username')
        password = data.get('password')
        usernameMail = data.get('username_mail')
        loginType = data.get('loginType')
        clientId = data.get('clientId')




        # Validar parámetros
        if username is None or password is None or clientId is None or loginType is None :
            return jsonify({"status": "Error", "code": 400,"message": getHttpStatusDescription(400)})
        # Conectar a la base de datos
        try:
            dbConnection.conn.connect()
            cursor = dbConnection.conn.cursor()


            # Construir consulta según loginType
            if loginType == 1:  # Login por usuario
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
                return jsonify({"status": "Error", "code": 400,"message": getHttpStatusDescription(400)})

            # Recuperar usuario
            user = cursor.fetchone()

        finally:
            # Asegurar desconexión de la base de datos
            dbConnection.conn.disconnect()

        if user:
            userId = user[0]
            storePasswordHash = user[4]

            # Validar contraseña
            if bcrypt.checkpw(password.encode('utf-8'), storePasswordHash.encode('utf-8')):
                # Verificar validez del token

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
                        token_info = {"status": "Ok", "code" : 200, "message": getHttpStatusDescription(200), "token": token, "tokenStart" : dateStart ,"tokenExpira": dateEndT}
                    else:
                        return jsonify({"status": "Error", "code": 406, "message": getHttpStatusDescription(406)})

                else:


                    token_info = {"status": "Ok","code" : 200, "message": getHttpStatusDescription(200), "token": checkValidityToken(userId)}

                return getUserInfo(clientId, userId, token_info)

            else:
                return jsonify({"status": "Error", "code": 402,"message": getHttpStatusDescription(402)})
        else:
            return jsonify({"status": "Error", "code": 401,"message": getHttpStatusDescription(401)})

    except Exception as e:
        # Manejo de errores 132.14.160.218
        return jsonify({"status": "Error", "code": 500, "message": getHttpStatusDescription(500)+": "+str(e)})



def getUserInfo(clientId, userId, token, langId):

    try:
        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor()

        sql = ("SELECT idUsuarios, idGrupo, usuario, nombre, apellido, clave,  mail, marca_cambio,"
               "telefono, observaciones FROM Usuarios "
               "WHERE estado = 1 AND idUsuarios = %s AND idEmpresa = %s")

        cursor.execute(sql, (userId, clientId))
        user = cursor.fetchone()

        if user:
            # Grupos
            sql = ("SELECT idGrupo, descripcion, observaciones, tipoGrupo FROM UsuariosGrupos where idGrupo = %s and estado = 1")
            cursor.execute(sql, (user[1],))
            grupos = cursor.fetchone()

            sql = ( "SELECT idPermiso, idGrupo, menu, alta, baja, modificacion FROM GruposPermisos where idGrupo = %s and estado = 1")
            cursor.execute(sql, (user[1],))
            gruposPermisos = cursor.fetchone()

            # Cliente
            sql = "select idEmpresa, prefijo, nombre, descripcion, domicilio, cuit, clientePropio from Empresas where idEmpresa = %s"
            cursor.execute(sql, (clientId,))
            cli = cursor.fetchone()



            # Accesos
            userAccess = getAccesByGrupo(clientId, grupos[0], user[0], langId)




            if not userAccess:
                userAccess = []

            # Construir respuesta

            grupos = {
                "id_grupo": grupos[0],
                "descripcion": grupos[1],
                "observaciones": grupos[2],
                "tipoGrupo": grupos[3],

            }

            gruposPermisos = {
                "id_permiso": gruposPermisos[0],
                "idGrupo": gruposPermisos[1],
                "menu": gruposPermisos[2],
                "alta": gruposPermisos[3],
                "baja": gruposPermisos,
                "modificacion": gruposPermisos[5],
            }
            gruposInfo={
                "grupos": grupos,
                "gruposPermisos": gruposPermisos,
            }

            company = {
                "id_cliente": cli[0],
                "prefijo": cli[1],
                "nombre": cli[2],
                "descripcion": cli[3],
                "domicilio": cli[4],
                "cuit": cli[5],
                "cliente_propio": cli[6],


            }





            userInfo = {
                "id_usuario": user[0],
                "usuario": user[2],
                "nombre_apellido": user[3]+" "+user[4],
                "email": user[6],
                "marca_cambio": user[7],
                "grupos": gruposInfo,
            }


            finalInfo = {
                "user": userInfo,
                "loginStatus": token,
                "company": company,


            }

            # Cierra conexión antes de devolver
            dbConnection.conn.close()
            dbConnection.conn.disconnect()

            finalInfo = utilities.Utilities.convertDateTimeToStr(finalInfo)
            final = json.dumps(finalInfo, indent=4, ensure_ascii=False)
            #print (final)
            return jsonify(finalInfo), 200

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

def getAccesByGrupo(clientId, groupId, userId, langId):
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
            if item["idPadre"] == 0:
                menus.append(item)
            else:
              if item["id_padre"] in elementos:
                        elementos[item["idPadre"]]["hijos"].append(item)
              else:
                print(
                     f"Advertencia: El id_padre {item['id_padre']} no existe en los elementos. Elemento: {item}")

        # Convertir a JSON
        #menu_json =  json.dumps(menu_jerarquico, indent=4, ensure_ascii=False)
        #print( json.dumps(menu_jerarquico, indent=4, ensure_ascii=False))
        menu_json = menus


        return menu_json




    except Exception as e:
          # Manejar cualquier excepción que ocurra

          print("Error al obtener los accesos y permisos:", e)
          return None

def checkPassword(hashedPassword, userPasswordTemp):
    # Compara la contraseña proporcionada con el hash almacenado
    return bcrypt.checkpw(userPasswordTemp.encode('utf-8'), hashedPassword)
def checkValidityToken(idUser):


    try:
        nowT = datetime.now()
        now = nowT.strftime('%Y-%m-%d %H:%M:%S')

        dbConnection.conn.connect()
        cursor = dbConnection.conn.cursor()
        sql = '''select id_accesos, token_tipo, token, fecha_desde, fecha_hasta from operadores_accesos where  id_operador = %s and fecha_hasta >= %s '''
        cursor.execute(sql, (idUser, now))

        valid = cursor.fetchall()
        if valid:
            for tok in valid:
                tokenInfo = {
                    "id" : tok[0],
                    "tokenType" : tok[1],
                    "token":  tok[2],
                    "start": tok[3],
                    "expira": tok[4]
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






def saveTokenAcces(user,   token):
    try:
        if user:
            user_id = user[0]
            stored_hashed_password = user[1]
            decodeToken = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            expirationTime = datetime.fromtimestamp(decodeToken['exp'])
            startDate = datetime.now()
            startDateTime = startDate.strftime('%Y-%m-%d %H:%M:%S')

            userId = decodeToken['id_operador']
            dbConnection.conn.connect()
            cursor = dbConnection.conn.cursor()
            sql = "INSERT INTO operadores_accesos (id_operador, token, dominio, fecha_desde, fecha_hasta, fecha_creacion, token_tipo) VALUES (%s, %s, %s,%s,%s,%s,%s)"
            cursor.execute(sql, (userId, token, "", startDateTime, expirationTime, startDateTime, "HASH256"))
            dbConnection.conn.commit()
            dbConnection.conn.disconnect()
            return True


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
        "description": "Conciliacion Bancaria.",
        "name": "Conciliacion Bancaria",
        "message": "Conciliacion Bancaria servicio de autentificacion funciona correctamente.",
        "functions": ["login", "recoverPassword", "logout"]
    }
    json_output = json.dumps(data, indent=4)
    logging.info(json_output)
    return json_output



if __name__ == '__main__':
    app.run(debug=True)
