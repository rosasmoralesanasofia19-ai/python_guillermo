from flask import Flask

app = Flask(__name__)

@app.route('/')
def inicio():
    return 'bienvenido a mi aplicacion Flask'

@app.route('/productos')
def productos():
    return 'lista de productos'
app.run(debug=True)
    