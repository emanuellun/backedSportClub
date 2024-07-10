#--------------------------------------------------------------------
# Instalar con pip install Flask
from flask import Flask, request, jsonify, render_template
from flask import request

# Instalar con pip install flask-cors
from flask_cors import CORS

# Instalar con pip install mysql-connector-python
import mysql.connector

# Si es necesario, pip install Werkzeug
from werkzeug.utils import secure_filename

# No es necesario instalar, es parte del sistema standard de Python
import os
import time
#--------------------------------------------------------------------


app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

#--------------------------------------------------------------------
class Cliente:
    #----------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        # Primero, establecemos una conexión sin especificar la base de datos
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        # Una vez que la base de datos está establecida, creamos la tabla si no existe
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            dni INT NOT NULL,
            edad INT NOT NULL,
            fecha_nac VARCHAR(255) NOT NULL,
            imagen_url VARCHAR(255),
            sede  VARCHAR(255) NOT NULL ''')
        self.conn.commit()

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)
        
    #----------------------------------------------------------------
    def agregar_cliente(self, dni, edad, nacimiento, imagen, sede):
            
        sql = "INSERT INTO clientes (dni, edad, fecha_nac, imagen_url, sede) VALUES (%s, %s, %s, %s, %s)"
        valores = (dni, edad, nacimiento, imagen, sede)

        self.cursor.execute(sql, valores)        
        self.conn.commit()
        return self.cursor.lastrowid

    #----------------------------------------------------------------
    def consultar_cliente(self, id):
        # Consultamos un cliente a partir de su id
        self.cursor.execute(f"SELECT * FROM clientes WHERE id = {id}")
        return self.cursor.fetchone()

    #----------------------------------------------------------------
    def modificar_cliente(self, id, nuevo_dni, nueva_edad, nueva_fecha, nueva_imagen, nueva_sede):
        sql = "UPDATE clientes SET dni = %s, edad = %s, fecha_nac = %s, imagen_url = %s, sede = %s WHERE id = %s"
        valores = (nuevo_dni, nueva_edad, nueva_fecha, nueva_imagen, nueva_sede, id)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def listar_clientes(self):
        self.cursor.execute("SELECT * FROM clientes")
        clientes = self.cursor.fetchall()
        return clientes

    #----------------------------------------------------------------
    def eliminar_cliente(self, id):
        # Eliminamos un cliente de la tabla a partir de su id
        self.cursor.execute(f"DELETE FROM clientes WHERE id = {id}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def mostrar_cliente(self, id):
        # Mostramos los datos de un cliente a partir de su id
        cliente = self.consultar_cliente(id)
        if cliente:
            print("-" * 40)
            print(f"id.....: {cliente['id']}")
            print(f"DNI: {cliente['dni']}")
            print(f"Edad...: {cliente['edad']}")
            print(f"Nacimiento.....: {cliente['fecha_nac']}")
            print(f"Imagen.....: {cliente['imagen_url']}")
            print(f"Sede..: {cliente['sede']}")
            print("-" * 40)
        else:
            print("cliente no encontrado.")


#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Cliente
#cliente = Cliente(host='localhost', user='root', password='root', database='miapp')
cliente = Cliente(host='emanuelluna99.mysql.pythonanywhere-services.com', user='emanuelluna99', password='Codo2024#', database='emanuelluna99$clientes')


# Carpeta para guardar las imagenes.
#RUTA_DESTINO = './static/imagenes/'

#Al subir al servidor, deberá utilizarse la siguiente ruta. USUARIO debe ser reemplazado por el nombre de usuario de Pythonanywhere
RUTA_DESTINO = '/home/emanuelluna99/mysite/static/imagenes'


#--------------------------------------------------------------------
# Listar todos los clientes
#--------------------------------------------------------------------
#La ruta Flask /clintes con el método HTTP GET está diseñada para proporcionar los detalles de todos los clientes almacenados en la base de datos.
#El método devuelve una lista con todos los clientes en formato JSON.
@app.route("/clientes", methods=["GET"]) #GET OBTENGO PRODUCTOS
def listar_cliente():
    clientes = cliente.listar_clientes()
    return jsonify(clientes)


#--------------------------------------------------------------------
# Mostrar un sólo cliente según su id
#--------------------------------------------------------------------
#La ruta Flask /clientes/<int:id> con el método HTTP GET está diseñada para proporcionar los detalles de un cliente específico basado en su código.
#El método busca en la base de datos el cliente con el id especificado y devuelve un JSON con los detalles del cliente si lo encuentra, o None si no lo encuentra.
@app.route("/clientes/<int:id>", methods=["GET"]) #GET OBTENGO PRODUCTOS
def mostrar_cliente(id):
    cliente= cliente.consultar_cliente(id)
    if cliente:
        return jsonify(cliente), 201
    else:
        return "cliente no encontrado", 404


#--------------------------------------------------------------------
# Agregar un cliente
#--------------------------------------------------------------------
@app.route("/clientes", methods=["POST"]) #POST AGREGO PRODUCTOS
#La ruta Flask `/clientes` con el método HTTP POST está diseñada para permitir la adición de un nuevo cliente a la base de datos.
#La función agregar_cliente se asocia con esta URL y es llamada cuando se hace una solicitud POST a /clientes.
def agregar_cliente():
    #Recojo los datos del form
    dni = request.form['dni']
    edad = request.form['edad']
    nacimiento = request.form['nacimiento']
    imagen = request.files['imagen']
    sede = request.form['sede']  
    nombre_imagen=""

    
    # Genero el nombre de la imagen
    nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
    nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

    nuevo_id = cliente.agregar_cliente(dni, edad, nacimiento, nombre_imagen, sede)
    if nuevo_id:    
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))

        #Si el cliente se agrega con éxito, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 201 (Creado).
        return jsonify({"mensaje": "Producto agregado correctamente.", "id": nuevo_id, "imagen": nombre_imagen}), 201
    else:
        #Si el cliente no se puede agregar, se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 500 (Internal Server Error).
        return jsonify({"mensaje": "Error al agregar el cliente."}), 500
    

#--------------------------------------------------------------------
# Modificar un cliente según su id
#--------------------------------------------------------------------
@app.route("/clientes/<int:id>", methods=["PUT"]) #ACTUALIZO LA INFORMACIÓN
#La ruta Flask /clientes/<int:id> con el método HTTP PUT está diseñada para actualizar la información de un producto existente en la base de datos, identificado por su código.
#La función modificar_cliente se asocia con esta URL y es invocada cuando se realiza una solicitud PUT a /productos/ seguido de un número (el código del producto).
def modificar_cliente(id):
    #Se recuperan los nuevos datos del formulario
    nuevo_dni = request.form.get("dni")
    nueva_edad = request.form.get("edad")
    nuevo_nacimiento = request.form.get("nacimiento")
    nueva_sede = request.form.get("sede")
    
    
    # Verifica si se proporcionó una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        # Procesamiento de la imagen
        nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
        nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

        # Guardar la imagen en el servidor
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        
        # Busco el cliente guardado
        cliente = cliente.consultar_cliente(id)
        if cliente: # Si existe el cliente...
            imagen_vieja = cliente["imagen_url"]
            # Armo la ruta a la imagen
            ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

            # Y si existe la ruta de imagen, la borro.
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    
    else:
        # Si no se proporciona una nueva imagen, simplemente usa la imagen existente del cliente
        cliente = cliente.consultar_producto(id)
        if cliente:
            nombre_imagen = cliente["imagen_url"]


    # Se llama al método modificar_cliente pasando el id del cliente y los nuevos datos.
    if cliente.modificar_cliente(id, nuevo_dni, nueva_edad, nuevo_nacimiento, nombre_imagen, nueva_sede):
        
        #Si la actualización es exitosa, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
        return jsonify({"mensaje": "Cliente modificado"}), 200
    else:
        #Si el cliente no se encuentra (por ejemplo, si no hay ningún producto con el código dado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Cliente no encontrado"}), 403



#--------------------------------------------------------------------
# Eliminar un cliente según su id
#--------------------------------------------------------------------
@app.route("/clientes/<int:id>", methods=["DELETE"])
#La ruta Flask /clientes/<int:id> con el método HTTP DELETE está diseñada para eliminar un cliente específico de la base de datos, utilizando su id como identificador.
#La función eliminar_cliente se asocia con esta URL y es llamada cuando se realiza una solicitud DELETE a /clientes/ seguido de un número (el id del cliente).
def eliminar_producto(id):
    # Busco el cliente en la base de datos
    cliente = cliente.consultar_cliente(id)
    if cliente: # Si el cliente existe, verifica si hay una imagen asociada en el servidor.
        imagen_vieja = cliente["imagen_url"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe la ruta de imagen, la elimina del sistema de archivos.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el cliente dela base de datos.
        if cliente.eliminar_cliente(id):
            #Si el cliente se elimina correctamente, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
            return jsonify({"mensaje": "Cliente eliminado"}), 200
        else:
            #Si ocurre un error durante la eliminación (por ejemplo, si el cliente no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
            return jsonify({"mensaje": "Error al eliminar el cliente"}), 500
    else:
        #Si el cliente no se encuentra (por ejemplo, si no existe un cliente con el id proporcionado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado). 
        return jsonify({"mensaje": "Cliente no encontrado"}), 404

#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)