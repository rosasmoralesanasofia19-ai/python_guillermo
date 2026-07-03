from flask import Flask

app = Flask(__name__)

@app.route('/contacto')
def contacto():
    return 'Página de contacto'     

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f"bienvenido, {nombre}"

app.run(debug=True)
