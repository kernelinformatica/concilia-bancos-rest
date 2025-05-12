HTTP_STATUS_CODES_ES = {
    200: "La autentificación fue existosa.",
    400: "La solicitud es incorrecta , está mal formada o hay un error en los parámetros recibidos.",
    401: "Las credenciales de atentificación son inválidas.",
    402: "Los datos proporcionados son inválidos.",
    403: "El usuario está autenticado, pero no tiene permiso para acceder al recurso solicitado.",
    404: "El recurso solicitado no se ha encontrado.",
    405: "El método HTTP utilizado no está permitido para el recurso solicitado.",
    406: "El token no se pudo registrar debido a un error inesperado.",
    500: "Se produjo un error interno en el servidor, inténte nuevamente más tarde."

}
HTTP_STATUS_CODES_EN = {
    200: "The authentication was successful.",
    400: "The request is incorrect, malformed, or there is an error in the parameters received.",
    401: "The authentication credentials are invalid.",
    402: "The data provided is invalid.",
    403: "The user is authenticated, but does not have permission to access the requested resource.",
    404: "The requested resource has not been found.",
    405: "The HTTP method used is not allowed for the requested resource.",
    406: "The token could not be registered due to an unexpected error.",
    500: "An internal error occurred on the server, please try again later."

}

# Ejemplo de uso en una función de manejo de errores
def getHttpStatusDescription(status_code, langId=1):
    if langId == 1:
        return HTTP_STATUS_CODES_ES.get(status_code, "Status")
    elif langId == 2:
        return HTTP_STATUS_CODES_EN.get(status_code, "Status")


#error_code = 401
#print(f"Código de Error: {error_code}, Descripción: {getHttpStatusDescription(error_code)}")
