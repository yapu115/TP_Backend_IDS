from flask import Flask, jsonify
from services import servicio_partidos

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '¡Hola, mundo! El servidor Flask está funcionando.'

@app.route('/partidos', methods=['GET'])
def obtener_partidos():
    partidos = servicio_partidos.obtener_todos_los_partidos()
    
    respuesta_json = [partido.to_dict() for partido in partidos]

    return jsonify(respuesta_json)

if __name__ == '__main__':
    app.run(debug=True)
