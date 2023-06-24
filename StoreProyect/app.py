from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'JostinYAnia12345'
app.config['MYSQL_DB'] = 'FlaskStore'
database = MySQL(app)

app.secret_key = "mysecretkey"

@app.route('/')
def Index():
    return render_template('index.html')

@app.route('/costumerAccount')
def CostumerAccount():
    return render_template('accountLogRe.html')


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
            return render_template('accountLogRe.html')
        else:
            cur = database.connection.cursor()
            cur.execute('INSERT INTO usuarios (Name, Lastname, Username, Email, Password) VALUES (%s, %s, %s, %s, %s)',
                        (name, lastname, username, email, password))
            database.connection.commit()
            flash('Usuario creado exitosamente')
            return render_template('accountLogRe.html')

def loginAccept(email, password):
    cur = database.connection.cursor()
    cur.execute('SELECT * FROM usuarios')
    data = cur.fetchall()

    for elem in data:
        if elem[4] == email and elem[5] == password:
            return True
        
    return False

      
@app.route('/loginUser', methods = ['POST', 'GET'])
def UserLogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if loginAccept(email, password):
            return redirect(url_for('UserIndex',email=email))
        else:
            flash('Usuario o contrasena incorrecta')

    return render_template('accountLogin.html')

@app.route('/user/index/<string:email>')
def UserIndex(email):
    flash('Bienvenido')
    return render_template('indexUser.html', email=email)

@app.route('/search', methods=['POST'])
def search():
    # Obtiene el término de búsqueda del cuerpo de la solicitud AJAX
    search_term = request.json['searchTerm']

    # Realiza la consulta a la base de datos para obtener los resultados
    cur = database.connection.cursor()
    query = f"SELECT * FROM articulos WHERE nombreArticulo LIKE '%{search_term}%'"
    cur.execute(query)
    results = cur.fetchall()

    productResults = [{'id': result[0], 'name': result[1]} for result in results]
    return jsonify(results=productResults)
    
@app.route('/searchProduct/<string:id>', methods=['GET', 'POST'])
def searchProduct(id):
    search_term = request.args.get('searchTerm')  # Obtener el término de búsqueda de los parámetros de la solicitud
    cur = database.connection.cursor()
    query = f"SELECT * FROM articulos WHERE nombreArticulo LIKE '%{search_term}%'"
    cur.execute(query)
    results = cur.fetchall()
    return render_template('productSearch.html', results=results)

@app.route('/TecnologiaYElectronicos')
def CategoriaTec():
    cur = database.connection.cursor()
    cur.execute("SELECT * FROM articuloscategoria")
    data = cur.fetchall()
    categoria = [{'id': result[0], 'nombre': result[1], 'precio': result[3], 'categoria_id' : result[2]} for result in data if result[2] == 1]
    return render_template('categoriaTecno.html', data=categoria)

@app.route('/electrodomesticos')
def CategoriaElectrod():
    cur = database.connection.cursor()
    cur.execute("SELECT * FROM articuloscategoria")
    data = cur.fetchall()
    categoria = [{'id': result[0], 'nombre': result[1], 'precio': result[3], 'categoria_id' : result[2]} for result in data if result[2] == 2]
    return render_template('categoriaElectro.html', data = categoria)

@app.route('/agregarCarrito/<string:id>', methods = ["POST", "GET"])
def AgregarCarrito(id):
    cur = database.connection.cursor()
    cur.execute("SELECT * FROM articuloscategoria")
    data = cur.fetchall()
    for producto in data:
        print(producto)


if __name__ == '__main__':
    app.run(port = 4000, debug=True)