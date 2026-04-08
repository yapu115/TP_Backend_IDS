from flask import Flask, jsonify, request
from services import servicio_partidos
from models.PartidoBase import PartidoBase

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '¡Hola, mundo! El servidor Flask está funcionando.'

@app.route('/partidos', methods=['GET'])
def obtener_partidos():
    partidos = servicio_partidos.obtener_todos_los_partidos()
    
    respuesta_json = [partido.to_dict() for partido in partidos]

    return jsonify(respuesta_json)

@app.route('/partidos', methods=['POST'])
def crear_partido():
    """
    Crear partido
    """
    datos = request.get_json()

    # Errores posibles (validación)
    if not datos:
        return jsonify({'error': "No se proporcionaron datos en la petición"}), 400

    campos_requeridos = ['equipo_local', 'equipo_visitante', 'fecha', 'fase']
    for campo in campos_requeridos:
        if campo not in datos:
            return jsonify({'error': f'Falta el campo obligatorio: {campo}'}), 400

    if datos['equipo_local'] == datos['equipo_visitante']:
        return jsonify({'error': 'El equipo local y visitante no pueden ser el mismo'}), 400


    # Creación del partido
    try:
        nuevo_partido = PartidoBase(
            equipo_local=datos['equipo_local'],
            equipo_visitante=datos['equipo_visitante'],
            fecha=datos['fecha'],
            fase=datos['fase'],
        )

        partido_creado = servicio_partidos.crear_partido(nuevo_partido)

        return jsonify({
        'mensaje': 'Partido creado exitosamente'
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 409
    
    except Exception as e:
        print(f"Error en el servidor: {e}")
        return jsonify({'error': 'Ocurrió un error interno en el servidor.'}), 500

    

    

if __name__ == '__main__':
    app.run(debug=True)
