import bcrypt

# Contraseña a hashear
password = "dario"
# Generar el hash de la contraseña
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
# Imprimir el hash generado
print("Hash generado:", hashed_password.decode('utf-8'))