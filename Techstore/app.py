from flask import Flask, render_template, request, jsonify  # type: ignore [import]
from database.conexion import obtener_conexion
from mysql.connector import Error

app = Flask(__name__)


# ==================== CONTROL DE CACHÉ ====================

@app.after_request
def sin_cache_formularios(response):
    """
    Evita que el navegador guarde en caché las páginas de registro y edición
    de productos. Así, al presionar 'atrás', el navegador vuelve a pedirle
    la página al servidor en lugar de mostrar una versión guardada.
    """
    rutas_sin_cache = ('/registro-producto', '/editar-producto')
    if request.path.startswith(rutas_sin_cache):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response


# ==================== PÁGINAS GENERALES ====================

@app.route('/')
def inicio():
    """Lista todos los productos registrados en la base de datos."""
    lista_productos = []
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM productos ORDER BY id DESC")
            lista_productos = cursor.fetchall()
    except Error as e:
        print(f"Error al listar productos: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return render_template('index1.html', productos=lista_productos)


@app.route('/contacto')
def contacto():
    return render_template('contacto.html')


@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')


@app.route('/servicios')
def servicios():
    return render_template('servicios.html')


@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html')


# ==================== API (ACTUALIZACIÓN EN TIEMPO REAL) ====================

@app.route('/api/productos')
def api_productos():
    """
    Devuelve la lista de productos en formato JSON.
    Usado por el frontend (JavaScript) para refrescar la vista de
    'Productos Destacados' sin recargar la página.
    """
    lista_productos = []
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM productos ORDER BY id DESC")
            lista_productos = cursor.fetchall()
    except Error as e:
        print(f"Error al obtener productos (API): {e}")
        return jsonify({"success": False, "productos": []}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return jsonify({"success": True, "productos": lista_productos})


# ==================== VALIDACIONES AUXILIARES ====================

def validar_precio(precio):
    """
    Valida que el precio sea un número válido y no negativo.
    Devuelve una tupla (precio_convertido, mensaje_error).
    Si mensaje_error es None, el precio es válido.
    """
    try:
        precio_valor = int(float(precio))
    except (TypeError, ValueError):
        return None, "El precio no puede ser negativo."

    if precio_valor < 0:
        return None, "El precio no puede ser negativo."

    return precio_valor, None


def codigo_duplicado(cursor, codigo, id_excluir=None):
    """
    Verifica si el código ya está registrado en otro producto.
    Si id_excluir se indica (modo edición), se ignora ese propio registro.
    """
    if id_excluir is None:
        cursor.execute("SELECT id FROM productos WHERE codigo = %s", (codigo,))
    else:
        cursor.execute("SELECT id FROM productos WHERE codigo = %s AND id != %s", (codigo, id_excluir))

    return cursor.fetchone() is not None


# ==================== CRUD DE PRODUCTOS ====================

@app.route('/productos')
def productos():
    """Lista todos los productos registrados en la base de datos."""
    lista_productos = []
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM productos ORDER BY id DESC")
            lista_productos = cursor.fetchall()
    except Error as e:
        print(f"Error al listar productos: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return render_template('productos.html', productos=lista_productos)


@app.route('/registro-producto')
def registro_producto():
    """Muestra el formulario para registrar un nuevo producto."""
    return render_template('registro_producto.html', producto=None)


@app.route('/editar-producto/<int:id>')
def editar_producto(id):
    """Muestra el formulario con los datos de un producto para editarlo."""
    producto = None
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
            producto = cursor.fetchone()
    except Error as e:
        print(f"Error al obtener producto: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

    return render_template('registro_producto.html', producto=producto)


@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    """Inserta un nuevo producto en la base de datos, con validaciones."""
    codigo = request.form.get('codigo')
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    categoria = request.form.get('categoria')

    if not codigo or not nombre or not precio or not categoria:
        return jsonify({"success": False, "message": "Todos los campos son obligatorios."}), 400

    # Validación del precio
    precio_valor, error_precio = validar_precio(precio)
    if error_precio:
        return jsonify({"success": False, "message": error_precio}), 400

    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        if conexion is None:
            return jsonify({"success": False, "message": "No se pudo conectar a la base de datos."}), 500

        cursor = conexion.cursor()

        # Validación del código duplicado
        if codigo_duplicado(cursor, codigo):
            return jsonify({"success": False, "message": "El código ya existe."}), 400

        cursor.execute(
            "INSERT INTO productos (codigo, nombre, precio, categoria) VALUES (%s, %s, %s, %s)",
            (codigo, nombre, precio_valor, categoria)
        )
        conexion.commit()
        return jsonify({"success": True, "message": "Producto registrado correctamente."})
    except Error as e:
        print(f"Error al guardar producto: {e}")
        # Código 1062: entrada duplicada (restricción UNIQUE de MySQL)
        if getattr(e, "errno", None) == 1062:
            return jsonify({"success": False, "message": "El código ya existe."}), 400
        return jsonify({"success": False, "message": "Error al guardar el producto."}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/actualizar_producto/<int:id>', methods=['POST'])
def actualizar_producto(id):
    """Actualiza los datos de un producto existente, con validaciones."""
    codigo = request.form.get('codigo')
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    categoria = request.form.get('categoria')

    if not codigo or not nombre or not precio or not categoria:
        return jsonify({"success": False, "message": "Todos los campos son obligatorios."}), 400

    # Validación del precio
    precio_valor, error_precio = validar_precio(precio)
    if error_precio:
        return jsonify({"success": False, "message": error_precio}), 400

    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        if conexion is None:
            return jsonify({"success": False, "message": "No se pudo conectar a la base de datos."}), 500

        cursor = conexion.cursor()

        # Validación del código duplicado (permite conservar el propio código)
        if codigo_duplicado(cursor, codigo, id_excluir=id):
            return jsonify({"success": False, "message": "El código ya existe."}), 400

        cursor.execute(
            "UPDATE productos SET codigo = %s, nombre = %s, precio = %s, categoria = %s WHERE id = %s",
            (codigo, nombre, precio_valor, categoria, id)
        )
        conexion.commit()
        return jsonify({"success": True, "message": "Producto actualizado correctamente."})
    except Error as e:
        print(f"Error al actualizar producto: {e}")
        # Código 1062: entrada duplicada (restricción UNIQUE de MySQL)
        if getattr(e, "errno", None) == 1062:
            return jsonify({"success": False, "message": "El código ya existe."}), 400
        return jsonify({"success": False, "message": "Error al actualizar el producto."}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


@app.route('/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto(id):
    """Elimina un producto de la base de datos."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        if conexion is None:
            return jsonify({"success": False, "message": "No se pudo conectar a la base de datos."}), 500

        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        conexion.commit()
        return jsonify({"success": True, "message": "Producto eliminado correctamente."})
    except Error as e:
        print(f"Error al eliminar producto: {e}")
        return jsonify({"success": False, "message": "Error al eliminar el producto."}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


if __name__ == '__main__':
    app.run(debug=True)