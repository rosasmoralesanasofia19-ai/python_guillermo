from flask import Flask

app = Flask(__name__)

@app.route('/')
def inicio():
    return '¡Hola, mundo con Flask!'

app.run(debug=True)


