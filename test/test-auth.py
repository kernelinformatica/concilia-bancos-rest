import requests


url = "http://127.0.0.1:5000/auth/login"

# Datos de prueba
payload = {
    'client' : '1',
    'username': 'dquiroga',
    'password': '12345',
    'username_mail' : 'darioquiroga@gmail.com',
    'login_type' : '1',
    'lang_id' : '2'
}

# Realiza la solicitud POST
response = requests.post(url, json=payload)

# Imprime la respuesta
print("Código de estado:", response.status_code)
print("Respuesta JSON:", response.json())
