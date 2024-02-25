from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_mysqldb import MySQL
from flask_login import login_manager, login_user, logout_user, login_required, LoginManager, current_user
from pagination import paginar_resultados




# Model UserMixin:
from modelUserMixin import User

# Diccionario de provincias y cantones
provincias_cantones = {
    "San Jose": ["San Jose", "Escazu" , "Desamparados", "Puriscal", "Tarrazu", "Aserri", "Mora", "Goicochea", "Santa Ana", "Alajuelita", "Vazquez de Coronado", "Acosta", "Tibas", "Moravia", "Montes de Oca", "Turrubares", "Dota", "curridabat", "Perez Zeledon", "Leon Cortes Castro"],

    "Cartago": ["Cartago", "Paraiso", "La Union", "Jimenez", "Turrialba", "Alvarado", "Oreamuno", "Guarco"],

    "Heredia" : ["Barva", "Belen", "Flores", "Heredia", "San Isidro", "San Pablo", "San Rafael", "Santa Barbara", "Santo Domingo", "Sarapiqui"],

    "Guanacaste" : ["Abangares", "Bagaces", "Canas", "Carrillo", "Hojacha", "La Cruz", "Liberia", "Nandayure", "Nicoya", "Santa Cruz", "Tilaran"],

    "Puntarenas" : ["Osa", "Corredores", "Coto Brus", "Esparza", "Garabito", "Golfito", "Montes de Oro", "Monteverde", "Osa", "Parrita", "Puerto Jimenez", "Puntarenas", "Quepos"],

    "Limon" : ["Guacimo", "Limon", "Matina", "Pococi", "Siquirres", "Talamanca"]
}

app = Flask(__name__)

"""
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'flaskstore'
database = MySQL(app)
"""
app.secret_key = "mysecretkey"
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def Index():
    cursor = database.connection.cursor()
    sqlProductos = "SELECT * FROM articuloscategoria"
    cursor.execute(sqlProductos)
    productos = cursor.fetchall()

    page = request.args.get('page', default=1, type=int)  # Obtiene el número de página de la URL

    total_elements = len(productos)

    per_page = 5  # Número de productos por página
    
    total_pages = (total_elements + per_page - 1) // per_page

    productos_pagina, pagination = paginar_resultados(productos, page, per_page)

    # Cálculo de prev_page y next_page
    if page > 1:
        prev_page = page - 1
    else:
        prev_page = 1

    if page < total_pages:
        next_page = page + 1
    else:
        next_page = page
    return render_template('index.html', productos=productos_pagina, pagination=pagination, total_pages = total_pages, prev_page = prev_page, next_page = next_page)

@app.route('/costumerAccount')
def CostumerAccount():
    return render_template('auth/accountLogRe.html')


def validateEmail(email):
    cur = database.connection.cursor()
    cur.execute('SELECT * FROM usuarios')
    data = cur.fetchall()
    for elemento in data:
        if elemento[4] == email:
            flash('El correo electrónico ya se encuentra registrado')
            return False  # Correo electrónico ya registrado, devuelve False
    return True  # Correo electrónico válido, devuelve True


@app.route('/userRegister', methods = ['POST'])
def UserRegister():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not validateEmail(email):
            return render_template('auth/accountLogRe.html')
        else:
            cur = database.connection.cursor()
            cur.execute('INSERT INTO usuarios (Name, Lastname, Username, Email, Password) VALUES (%s, %s, %s, %s, %s)',
                        (name, lastname, username, email, password))
            database.connection.commit()
            flash('Usuario creado exitosamente')
            return render_template('auth/accountLogRe.html')

def loginAccept(email, password):
    cur = database.connection.cursor()
    cur.execute('SELECT * FROM usuarios')
    data = cur.fetchall()

    for elem in data:
        if elem[8] == email and elem[9] == password:
            return True
        
    return False

@login_manager.user_loader
def load_user(user_id):
    user_data = getUserByID(user_id)
    if user_data is not None:
        user = User(user_data[0], user_data[1], user_data[2], user_data[3])  # Crear el objeto User utilizando los datos obtenidos
        return user
    else:
        return None

def getUserByID(id):
    try:
        cursor = database.connection.cursor()
        sql = """SELECT id, Name, Lastname, Username FROM usuarios WHERE id = {}""".format(id)
        cursor.execute(sql)
        data = cursor.fetchone()

        if data is not None:
            return data
        else:
            return None    
    
    except Exception as ex:
        raise Exception(ex)

def getUserByEmail(email):
    try:
        cursor = database.connection.cursor()
        sql = "SELECT id, Name, Lastname, Username FROM usuarios WHERE Email = %s"
        cursor.execute(sql, (email,))
        data = cursor.fetchone()

        if data is not None:
            return data
        else:
            return None

    except Exception as ex:
        raise Exception(ex)

@app.route('/loginUser', methods = ['POST', 'GET'])
def UserLogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if loginAccept(email, password):
            userData = getUserByEmail(email)
            if userData is not None:
                userID = userData[0]
                user = User(userData[0], userData[1], userData[2], userData[3])
                login_user(user)
                return redirect(url_for('UserIndex'))
        flash('Usuario o contrasena incorrecta')

    return render_template('auth/accountLogin.html')

@app.route('/user/index/')
@login_required
def UserIndex():
    flash('Bienvenido')
    cursor = database.connection.cursor()
    sql = """SELECT * FROM carrito WHERE id_usuario = {}""".format(current_user.id)
    cursor.execute(sql)
    dataCarrito = cursor.fetchall()
    totalAmount = 0
    for data in dataCarrito:
        totalAmount += int(data[2])
    
    sqlProductos = "SELECT * FROM articuloscategoria"
    cursor.execute(sqlProductos)
    productos = cursor.fetchall()
    page = request.args.get('page', default=1, type=int)  # Obtiene el número de página de la URL
    total_elements = len(productos)
    per_page = 5  # Número de productos por página
    total_pages = (total_elements + per_page - 1) // per_page

    productos_pagina, pagination = paginar_resultados(productos, page, per_page)

    # Cálculo de prev_page y next_page
    if page > 1:
        prev_page = page - 1
    else:
        prev_page = 1

    if page < total_pages:
        next_page = page + 1
    else:
        next_page = page

    cursor.close()
    session['dataCarrito'] = dataCarrito
    session['rutaAnterior'] = '/user/index/'
    session['totalAmount'] = totalAmount
    return render_template('userLoggued/base.html', dataCarr = dataCarrito, totalAmount = totalAmount, productos=productos_pagina, pagination=pagination, total_pages = total_pages, prev_page = prev_page, next_page = next_page)

@app.route('/user/index/profile')
@login_required
def UserIndexProfile():
    session['rutaAnterior'] = '/user/index/profile'
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')
    return render_template('userLoggued/userAccount.html', dataCarr = dataCarrito, totalAmount = totalAmount)

@app.route('/user/index/MyProfile')
@login_required
def UserMyProfile():
    session['rutaAnterior'] = '/user/index/MyProfile'
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')
    cursor = database.connection.cursor()
    sql = """SELECT * FROM usuarios WHERE id = {}""".format(current_user.id)
    cursor.execute(sql)
    infoUser = cursor.fetchall()

    for data in infoUser:
        provinciaUsuario = data[5]
        cantonUsuario = data[6]
        dirrecionUsuario = data[7]
        break

    sqlProvincia = "SELECT * FROM provincias"
    cursor.execute(sqlProvincia)
    dataProvincia = cursor.fetchall()

    for data in dataProvincia:
        if str(data[0]) == provinciaUsuario:
            provinciaUsuario = data[1]
            print(provinciaUsuario)
            break

    sqlCantones = "SELECT * FROM cantones"
    cursor.execute(sqlCantones)
    dataCanton = cursor.fetchall()

    for data in dataCanton:
        if str(data[0]) == cantonUsuario:
            cantonUsuario = data[2]
            print(cantonUsuario)
            break

    cursor.close()
    return render_template('userLoggued/userIndexProfileMenu/MyProfile.html', dataCarr = dataCarrito, totalAmount = totalAmount, infoUsuario = infoUser, provinciaUsuario = provinciaUsuario, cantonUsuario = cantonUsuario, dirrecionUsuario = dirrecionUsuario)

@app.route("/user/index/MyProfile/UpdateInfo" , methods = ['POST', 'GET'])
@login_required
def UpdateInfoUser():
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')
    if request.method == "POST":
        nombre = request.form["name"]
        apellido = request.form['lastname']
        correoElectronico = request.form['email']
        cursor = database.connection.cursor()
        try:
            sql = """UPDATE usuarios SET Name = %s, Lastname = %s, Email = %s WHERE id = %s"""
            cursor.execute(sql , (nombre, apellido, correoElectronico, current_user.id))
            database.connection.commit()
        except Exception as e:
            print("Error:", e)
            database.connection.rollback()
        finally:
            cursor.close()
    return render_template('userLoggued/userIndexProfileMenu/UpdateInfoCliente.html', dataCarr = dataCarrito, totalAmount = totalAmount)

@app.route("/user/index/MyProfile/UpdateInfo/Adresses", methods = ["POST", "GET"])
@login_required
def UpdateInfoUserAdresses():
    cantones = []
    provinciaUsuario = ""    
    cantonUsuario = "" 
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')

    if request.method == 'POST':
        provinciaUsuario = request.form['provincia']
        cantonUsuario = request.form['canton']
        direccionUsuario = request.form['dirreccion']
    
        cursorProvincia = database.connection.cursor()
        sqlDataProvincia = "SELECT * FROM provincias"
        cursorProvincia.execute(sqlDataProvincia)
        dataProvincia = cursorProvincia.fetchall()

        cursorCanton = database.connection.cursor()
        sqlDataCanton = "SELECT * FROM cantones"
        cursorCanton.execute(sqlDataCanton)
        dataCanton = cursorCanton.fetchall()

        provinciaDataBase = ""
        for provincia in dataProvincia:
            if provincia[1] == provinciaUsuario:
                provinciaDataBase = provincia[0]
                print(provinciaDataBase)
                break

        cantonDataBase = ""
        for canton in dataCanton:
            if canton[2] == cantonUsuario:
                cantonDataBase = canton[0]
                print(cantonDataBase)
                break

        #consulta y update en database
        cursorUserTable = database.connection.cursor()
        sql = "UPDATE usuarios SET Provincia = %s, Canton = %s, Direccion = %s WHERE id = %s"
        try:
            cursorUserTable.execute(sql, (provinciaDataBase, cantonDataBase, direccionUsuario, current_user.id))
            database.connection.commit()
        except Exception as e:
            print("Error:", e)
            database.connection.rollback()
        finally:
            cursorUserTable.close()

    
    if provinciaUsuario:
        cantones = provincias_cantones.get(provinciaUsuario, [])

    return render_template('userLoggued/userIndexProfileMenu/UpdateDirecciones.html', provincias = provincias_cantones.keys(), cantones = cantones, provinciaUsuario = provinciaUsuario, cantonUsuario = cantonUsuario, dataCarr = dataCarrito, totalAmount = totalAmount)


@app.route('/user/index/MyOrders')
@login_required
def UserMyOrders():
    session['rutaAnterior'] = '/user/index/MyOrders'
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')
    return render_template('userLoggued/userIndexProfileMenu/Mispedidos.html', dataCarr = dataCarrito, totalAmount = totalAmount)

@app.route('/user/index/MyWhichList')
@login_required
def UserMyWhichList():
    session['rutaAnterior'] = '/user/index/MyWhichList'
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')

    cur = database.connection.cursor()
    cur.execute("SELECT * FROM listadeseos")
    data = cur.fetchall()
    print(data)
    return render_template('userLoggued/userIndexProfileMenu/MilistaDeseos.html', dataCarr = dataCarrito, totalAmount = totalAmount, data = data)

@app.route('/user/index/MyAdresses')
@login_required
def UserMyAdresses():
    session['rutaAnterior'] = '/user/index/MyAdresses'
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')

    cursor = database.connection.cursor()
    sqlUsuario = "SELECT * FROM usuarios WHERE id = {}".format(current_user.id)
    sqlProvincias = "SELECT * FROM provincias"
    sqlCantones = "SELECT * FROM cantones"

    cursor.execute(sqlUsuario)
    dataUser = cursor.fetchall()

    
    cursor.execute(sqlProvincias)
    dataProvincias = cursor.fetchall()


    cursor.execute(sqlCantones)
    dataCantones = cursor.fetchall()
    cursor.close()

    cantonDataBase = ""
    provinciaDataBase = ""
    direccionDataBase = ""

    for data in dataUser:
        provinciaDataBase = data[5]
        cantonDataBase = data[6]
        direccionDataBase = data[7]
        break

    for dataProvincia in dataProvincias:
        if str(dataProvincia[0]) == provinciaDataBase:
            provinciaDataBase = dataProvincia[1]
            break
    for dataCanton in dataCantones:
        if str(dataCanton[0]) == cantonDataBase:
            cantonDataBase = dataCanton[2]
            break

    return render_template('userLoggued/userIndexProfileMenu/MisDirecciones.html', dataCarr = dataCarrito, totalAmount = totalAmount, provinciaDataBase = provinciaDataBase, cantonDataBase = cantonDataBase, direccionDataBase = direccionDataBase)

@app.route('/Logout')
@login_required
def UserLogout():
    logout_user()
    return redirect(url_for('Index'))


@app.route('/user/index/CategoriaTecnologia' , methods = ['POST', 'GET'])
def userLogguedCatTec():
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')
    dataProducto = []
    cur = database.connection.cursor()
    cur.execute("SELECT * FROM articuloscategoria")
    data = cur.fetchall()

    for producto in data:
        if producto[2] == 1:
            dic = {}
            dic['id'] = producto[0]
            dic['nombre'] = producto[1]
            dic['precio'] = producto[3]
            dataProducto.append(dic)

    pageCatTec = request.args.get('page', default=1, type=int)  # Obtiene el número de página de la URL
    total_elements = len(dataProducto)
    per_page = 4  # Número de productos por página
    totalPages = (total_elements + per_page - 1) // per_page

    productos_pagina, pagination = paginar_resultados(dataProducto, pageCatTec, per_page)
    # Cálculo de prev_page y next_page
    if pageCatTec > 1:
        prevPage = pageCatTec - 1
    else:
        prevPage = 1

    if pageCatTec < totalPages:
        nextPage = pageCatTec + 1
    else:
        nextPage = pageCatTec
    
    return render_template('userLoggued/catTecUserL.html', dataCarr=dataCarrito, totalAmount=totalAmount, productos=productos_pagina, pagination=pagination, totalPages = totalPages, prevPage = prevPage, nextPage = nextPage, page = pageCatTec)

@app.route('/user/index/CategoriaElectrodomesticos')
def userLogguedCatElectro():
    cur = database.connection.cursor()
    cur.execute("SELECT * FROM articuloscategoria")
    data = cur.fetchall()

    categoria = [{'id': result[0], 'nombre': result[1], 'precio': result[3], 'categoria_id' : result[2]} for result in data if result[2] == 2]
    pageCatTec = request.args.get('page', default=1, type=int)  # Obtiene el número de página de la URL
    total_elements = len(categoria)
    per_page = 4  # Número de productos por página
    totalPages = (total_elements + per_page - 1) // per_page

    productos_pagina, pagination = paginar_resultados(categoria, pageCatTec, per_page)
    # Cálculo de prev_page y next_page
    if pageCatTec > 1:
        prevPage = pageCatTec - 1
    else:
        prevPage = 1

    if pageCatTec < totalPages:
        nextPage = pageCatTec + 1
    else:
        nextPage = pageCatTec
    
    session['rutaAnterior'] = '/user/index/CategoriaElectrodomesticos'
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')
    return render_template('userLoggued/catElectroUserL.html', data=categoria, dataCarr=dataCarrito, totalAmount=totalAmount,  productos=productos_pagina, pagination=pagination, totalPages = totalPages, prevPage = prevPage, nextPage = nextPage, page = pageCatTec)
     
@app.route('/user/index/CategoriaHogar')
def userLogguedCatHogar():
    cur = database.connection.cursor()
    cur.execute("SELECT * FROM articuloscategoria")
    data = cur.fetchall()
    categoria = [{'id': result[0], 'nombre': result[1], 'precio': result[3], 'categoria_id' : result[2]} for result in data if result[2] == 3]
    pageCatTec = request.args.get('page', default=1, type=int)  # Obtiene el número de página de la URL
    total_elements = len(categoria)
    per_page = 4  # Número de productos por página
    totalPages = (total_elements + per_page - 1) // per_page

    productos_pagina, pagination = paginar_resultados(categoria, pageCatTec, per_page)
    # Cálculo de prev_page y next_page
    if pageCatTec > 1:
        prevPage = pageCatTec - 1
    else:
        prevPage = 1

    if pageCatTec < totalPages:
        nextPage = pageCatTec + 1
    else:
        nextPage = pageCatTec
    session['rutaAnterior'] = '/user/index/CategoriaHogar'
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')
    return render_template('userLoggued/catHogarUserL.html', data = categoria, dataCarr = dataCarrito, totalAmount=totalAmount, productos=productos_pagina, pagination=pagination, totalPages = totalPages, prevPage = prevPage, nextPage = nextPage, page = pageCatTec)


@app.route('/search', methods=['POST'])
def search():
    # Obtiene el término de búsqueda del cuerpo de la solicitud AJAX
    search_term = request.json['searchTerm']

    # Realiza la consulta a la base de datos para obtener los resultados
    cur = database.connection.cursor()
    query = f"SELECT * FROM articuloscategoria WHERE nombre LIKE '%{search_term}%'"
    cur.execute(query)
    results = cur.fetchall()

    productResults = [{'id': result[0], 'name': result[1]} for result in results]
    return jsonify(results=productResults)
    
@app.route('/searchProduct/<string:id>', methods=['GET', 'POST'])
def searchProduct(id):
    search_term = request.args.get('searchTerm')  # Obtener el término de búsqueda de los parámetros de la solicitud
    print(id)
    cur = database.connection.cursor()
    query = "SELECT * FROM articuloscategoria WHERE id LIKE {}".format(id)
    cur.execute(query)
    results = cur.fetchall()
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')
    return render_template('productSearch.html', results=results, dataCarr = dataCarrito, totalAmount=totalAmount)

@app.route('/user/index/searchProduct/<string:id>', methods=['GET', 'POST'])
@login_required
def searchProductUserLog(id):
    cur = database.connection.cursor()
    query = "SELECT * FROM articuloscategoria WHERE id LIKE {}".format(id)
    cur.execute(query)
    results = cur.fetchall()
    dataCarrito = session.get('dataCarrito')
    totalAmount = session.get('totalAmount')
    return render_template('userLoggued/productSearchUser.html', results=results, dataCarr = dataCarrito, totalAmount=totalAmount)

@app.route('/TecnologiaYElectronicos', methods = ["GET", "POST"])
def CategoriaTec(): #Index principal
    cur = database.connection.cursor()
    cur.execute("SELECT * FROM articuloscategoria")
    data = cur.fetchall()
    categoria = [{'id': result[0], 'nombre': result[1], 'precio': result[3], 'categoria_id' : result[2]} for result in data if result[2] == 1]
    pageCatTec = request.args.get('page', default=1, type=int)  # Obtiene el número de página de la URL
    total_elements = len(categoria)
    per_page = 4  # Número de productos por página
    totalPages = (total_elements + per_page - 1) // per_page

    productos_pagina, pagination = paginar_resultados(categoria, pageCatTec, per_page)
    # Cálculo de prev_page y next_page
    if pageCatTec > 1:
        prevPage = pageCatTec - 1
    else:
        prevPage = 1

    if pageCatTec < totalPages:
        nextPage = pageCatTec + 1
    else:
        nextPage = pageCatTec

    return render_template('categoriaTecno.html', data=categoria, productos=productos_pagina, pagination=pagination, totalPages = totalPages, prevPage = prevPage, nextPage = nextPage, page = pageCatTec)

@app.route('/electrodomesticos')
def CategoriaElectrod():#Index principal
    cur = database.connection.cursor()
    cur.execute("SELECT * FROM articuloscategoria")
    data = cur.fetchall()
    categoria = [{'id': result[0], 'nombre': result[1], 'precio': result[3], 'categoria_id' : result[2]} for result in data if result[2] == 2]
    pageCatTec = request.args.get('page', default=1, type=int)  # Obtiene el número de página de la URL
    total_elements = len(categoria)
    per_page = 4  # Número de productos por página
    totalPages = (total_elements + per_page - 1) // per_page

    productos_pagina, pagination = paginar_resultados(categoria, pageCatTec, per_page)
    # Cálculo de prev_page y next_page
    if pageCatTec > 1:
        prevPage = pageCatTec - 1
    else:
        prevPage = 1

    if pageCatTec < totalPages:
        nextPage = pageCatTec + 1
    else:
        nextPage = pageCatTec

    return render_template('categoriaElectro.html', data = categoria, productos=productos_pagina, pagination=pagination, totalPages = totalPages, prevPage = prevPage, nextPage = nextPage, page = pageCatTec)

@app.route('/Hogar')
def CategoriaHogar():
    cur = database.connection.cursor()
    cur.execute("SELECT * FROM articuloscategoria")
    data = cur.fetchall()
    categoria = [{'id': result[0], 'nombre': result[1], 'precio': result[3], 'categoria_id' : result[2]} for result in data if result[2] == 3]
    pageCatTec = request.args.get('page', default=1, type=int)  # Obtiene el número de página de la URL
    total_elements = len(categoria)
    per_page = 4  # Número de productos por página
    totalPages = (total_elements + per_page - 1) // per_page

    productos_pagina, pagination = paginar_resultados(categoria, pageCatTec, per_page)
    # Cálculo de prev_page y next_page
    if pageCatTec > 1:
        prevPage = pageCatTec - 1
    else:
        prevPage = 1

    if pageCatTec < totalPages:
        nextPage = pageCatTec + 1
    else:
        nextPage = pageCatTec
    return render_template('categoriaHogar.html', data = categoria, productos=productos_pagina, pagination=pagination, totalPages = totalPages, prevPage = prevPage, nextPage = nextPage, page = pageCatTec)


@app.route('/agregarCarrito/<string:id>', methods=["POST", "GET"])
@login_required
def AgregarCarrito(id):
    cur = database.connection.cursor()
    cur.execute('SELECT * FROM articuloscategoria WHERE id = %s', (id,))
    data = cur.fetchall()
    print(data)
    for producto in data:
        nombre = producto[1]
        idCategoria = producto[2]
        precio = producto[3]
        cur.execute('INSERT INTO carrito (nombre, id_categoria, precio, id_usuario) VALUES (%s, %s, %s, %s)', (nombre, idCategoria, precio, current_user.id,))    
        database.connection.commit()
    flash('Producto agregado al carrito')


    cur = database.connection.cursor()
    cur.execute('SELECT * FROM carrito WHERE id_usuario = %s', (current_user.id,))
    dataCarrito = cur.fetchall()
    totalAmount = sum(int(data[2]) for data in dataCarrito)

    # Almacenar los datos actualizados en la sesión del usuario
    session['dataCarrito'] = dataCarrito
    session['totalAmount'] = totalAmount
    return redirect(request.referrer)

@app.route('/ComprarProducto/<string:id>', methods = ['POST', 'GET'])
@login_required
def ComprarProducto(id):
    cursor = database.connection.cursor()
    sql = """SELECT * FROM carrito WHERE id_usuario = {}""".format(current_user.id)
    cursor.execute(sql)
    dataProducto = cursor.fetchall()
    for data in dataProducto:
        if str(data[0]) == id:
            dataProducto = data
    print(dataProducto)
    return render_template('userLoggued/compraProducto.html')

@app.route('/AgregarListaDeDeseos/<string:id>', methods=["POST", "GET"])
@login_required
def AgregarListaDeDeseos(id):
    cur = database.connection.cursor()
    cur.execute('SELECT * FROM articuloscategoria WHERE id = %s', (id,))
    data = cur.fetchall()
    for producto in data:
        id = producto[0]
        nombre = producto[1]
        idCategoria = producto[2]
        precio = producto[3]
        cur.execute('INSERT INTO listaDeseos (id, nombre, id_categoria, precio, id_usuario) VALUES (%s, %s, %s, %s, %s)', (id, nombre, idCategoria, precio, current_user.id,))    
        database.connection.commit()
        cur.close()
    flash('Producto agregado a la lista de deseos')
    return redirect(request.referrer)

@app.route('/deleteProduct/<string:id>')
def DeleteProductCarrito(id):
    cur = database.connection.cursor()
    sql = """DELETE FROM carrito WHERE id = %s"""
    cur.execute(sql, (id,))
    database.connection.commit()
    cur.close()
    flash('Producto Eliminado')

    cur = database.connection.cursor()
    cur.execute('SELECT * FROM carrito WHERE id_usuario = %s', (current_user.id,))
    dataCarrito = cur.fetchall()
    totalAmount = sum(int(data[2]) for data in dataCarrito)

    # Almacenar los datos actualizados en la sesión del usuario
    session['dataCarrito'] = dataCarrito
    session['totalAmount'] = totalAmount

    return redirect(request.referrer)


# Manejo de errores:
def Estatus401(error):
    return redirect(url_for('UserLogin'))

def Estatus404(error):
    return redirect(url_for('Index'))

if __name__ == '__main__':
    app.register_error_handler(401, Estatus401)
    app.register_error_handler(404, Estatus404)
    app.run(port = 4000, debug=True)
    