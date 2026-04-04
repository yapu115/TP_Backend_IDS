from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '¡Hola, mundo! El servidor Flask está funcionando.'

if __name__ == '__main__':
    app.run(debug=True)
