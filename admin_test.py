# db.administradores.insertOne({
#   usuario: "admin01",
#   password_hash: "$2b$12$fvP58jozUrDM7ILIFxPwkulUi/vmexrEek7RQCL9aJI6TX5a46GlW",
#   nombre: "Administrador Principal",
#   email: "admin@example.com",
#   rol: "super_admin",
#   activo: true,
#   fecha_creacion: new Date(),
#   fecha_actualizacion: new Date(),
#   ultimo_login: null
# })
import bcrypt

# Contraseña en texto plano
password = "nico2004"

# Generar salt y hashear
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Convertirlo a string para guardarlo en MongoDB (opcional pero común)
password_hash_str = password_hash.decode('utf-8')

print(password_hash_str)
