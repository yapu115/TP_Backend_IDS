from flask import Flask, jsonify, request, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from services import servicio_partidos, servicios_usuarios
from utils.errores import error_respuesta
from models.PartidoBase import PartidoBase

app = Flask(__name__)

# Swagger Config
SWAGGER_URL = '/api/docs'
API_URL = '/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API TP_Backend_IDS"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def hello_world():
    return '¡Hola, mundo! El servidor Flask está funcionando.'

@app.route('/swagger.yaml')
def serve_swagger_yaml():
    return send_from_directory('.', 'swagger.yaml')

@app.route('/partidos', methods=['GET'])
def obtener_partidos():

    equipo = request.args.get('equipo')
    fecha = request.args.get('fecha')
    fase = request.args.get('fase')
    _limit = request.args.get('_limit', type=int) 
    _offset = request.args.get('_offset', default=0, type=int)

    if _limit is not None and _limit <= 0:
        return jsonify({'error': 'El límite (_limit) debe ser un número mayor a 0'}), 400

    if _offset < 0:
        return jsonify({'error': 'El desplazamiento (_offset) no puede ser negativo'}), 400

    if fecha is not None:
        from datetime import datetime
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'La fecha debe cumplir el formato ISO 8601 (YYYY-MM-DD)'}), 400

    if fase is not None and fase not in ['Fase de grupos', 'Octavos de final', 'Cuartos de final', 'Semifinal', 'Final']:
        return jsonify({'error': 'La fase no es válida'}), 400

    partidos, total = servicio_partidos.obtener_todos_los_partidos(
        equipo=equipo, 
        fecha=fecha, 
        fase=fase, 
        _limit=_limit,
        _offset=_offset
    )
    
    if not partidos and total == 0:
        return '', 204
    
    respuesta_json = [partido.to_dict() for partido in partidos]
    
    # Si se solicitó paginación, armamos los links HATEOAS
    if _limit is not None:
        # urlencode es para obtener los parametros de la peticion en formato string a partir de un diccionario
        from urllib.parse import urlencode
        
        args = request.args.copy()
        url_base = request.base_url

        def construir_url(offset_val):
            args_copy = args.copy()
            args_copy['_offset'] = offset_val
            args_copy['_limit'] = _limit
            return f"{url_base}?{urlencode(args_copy)}"

        last_page_offset = max(0, (total - 1) // _limit * _limit) if total > 0 else 0

        # Se comienza a construir el diccionario con los links
        links = {
            '_first': construir_url(0),
            '_last': construir_url(last_page_offset)
        }

        if _offset > 0:
            links['_prev'] = construir_url(max(0, _offset - _limit))

        if _offset + _limit < total:
            links['_next'] = construir_url(_offset + _limit)

        return jsonify({
            'resultados': respuesta_json,
            '_links': links
        }), 200


    return jsonify(respuesta_json), 200


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

    if datos['fase'] not in ['grupos', 'dieciseisavos', 'octavos', 'cuartos', 'semis', 'final']:
        return jsonify({'error': 'La fase no es válida'}), 400


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

#GET partidos
@app.route('/partidos/<int:id>', methods=['GET'])
def obtener_partido_por_id(id):
    try:
        if id <= 0:
            # Swagger: 400 con schema Errores
            return jsonify({
                "errors": [{
                    "code": "BAD_REQUEST",
                    "message": "El id debe ser mayor que 0",
                    "level": "error",
                    "description": "El parámetro de ruta id debe ser un entero positivo."
                }]
            }), 400

        partido = servicio_partidos.obtener_partido_por_id(id)

        if partido is None:
            # Swagger: 404 con schema Errores
            return jsonify({
                "errors": [{
                    "code": "NOT_FOUND",
                    "message": "Partido no encontrado",
                    "level": "error",
                    "description": f"No existe un partido con id={id}."
                }]
            }), 404

        return jsonify(partido), 200

    except Exception as e:
        print(f"Error en el servidor: {e}")
        # Swagger: 500 con schema Errores
        return jsonify({
            "errors": [{
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Error interno del servidor",
                "level": "error",
                "description": "Ocurrió un error inesperado procesando la solicitud."
            }]
        }), 500
 
#PUT DE RESULTADOS
@app.route('/partidos/<int:id>/resultado', methods=["PUT"])
def actualizar_resultado(id):
    try:

        datos = request.get_json()

        #POSIBLES ERRORES  
        if datos is None:
           return error_respuesta("error: Debe enviar un JSON", 400)
    
        if "goles_local" not in datos or "goles_visitante" not in datos:
           return error_respuesta("Error: Faltan goles_local o goles_visitante", 400)

        if id<=0:
            return error_respuesta("El id debe ser mayor que 0", 400)

        try: 
            goles_local = int(datos["goles_local"])
            goles_visitante = int(datos["goles_visitante"])
        except:
            return error_respuesta("Los goles deben ser números enteros", 400)
 
        if goles_local < 0 or goles_visitante < 0:
            return error_respuesta("Los goles no pueden numeros negativos", 400)  

        partido_actualizado = servicio_partidos.actualizar_resultado(id, goles_local, goles_visitante)
      
        if partido_actualizado is None:
            return error_respuesta("Partido no encontrado",404)

        return jsonify(partido_actualizado), 200

    except Exception as e:
        return error_respuesta(f"Error interno del servidor: {str(e)}", 500) 


#PUT DE PARTIDOS
def texto_valido(valor):
    if not isinstance(valor,str):
        return False

    valor = valor.strip()

    if valor == "":
        return False
    
    try:
        float(valor)
        return False
    except:
        return True

@app.route('/partidos/<int:id>', methods=["PUT"])

def actualizar_partidos(id):
    try:
        datos = request.get_json()

        if datos is None:
            return error_respuesta("Debes enviar un JSON", 400)

        if id <= 0:
            return error_respuesta("El id debe ser mayor que 0", 400)    

        campos_obligatorios = [
            "equipo_local",
            "equipo_visitante",
            "fecha",
            "fase",
            "estadio",
            "ciudad"
        ]

        for campo in campos_obligatorios:
            if campo not in datos:
                return error_respuesta("Falta el campo {campo}", 400)

        equipo_local = datos["equipo_local"]
        equipo_visitante = datos["equipo_visitante"]
        fecha = datos["fecha"]
        fase = datos["fase"]
        estadio = datos["estadio"]
        ciudad = datos["ciudad"]

        #POSIBLES ERRORES
        if str(equipo_local).strip() == "":
            return error_respuesta("El equipo local no puede estar vacio", 400)
           
        if str(equipo_visitante).strip() == "":
            return error_respuesta("El equipo visitante no puede estar vacio", 400)
          
        if str(fase).strip() == "":
           return error_respuesta("La fase no puede estar vacia", 400)    

        if str(estadio).strip() == "":
           return error_respuesta("El estadio no puede estar vacia", 400)  

        if str(ciudad).strip() == "":
           return error_respuesta("La ciudad no puede estar vacia", 400)  

        if not texto_valido(equipo_local):
            return error_respuesta("El equipo local debe ser un texto", 400)

        if not texto_valido(equipo_visitante):
            return error_respuesta("El equipo visitante debe ser un texto", 400)

        if not texto_valido(fase):
            return error_respuesta("La fase debe ser un texto", 400)

        if not texto_valido(estadio):
            return error_respuesta("El estadio debe ser un texto", 400)
        
        if not texto_valido(ciudad):
            return error_respuesta("La ciudad debe ser un texto", 400)

        equipo_local = str(datos["equipo_local"].strip())
        equipo_visitante = str(datos["equipo_visitante"].strip())
        fecha = str(datos["fecha"].strip())
        fase = str(datos["fase"].strip())
        estadio = str(datos["estadio"].strip())
        ciudad = str(datos["ciudad"].strip())

        if fecha == "":
            return error_respuesta("La fecha no puede estar vacía",400)

        if equipo_local.lower() == equipo_visitante.lower():
            return error_respuesta("El equipo local y el visitante no pueden ser iguales", 400)

        partido_actualizado = servicio_partidos.actualizar_partidos(
            id, 
            equipo_local,
            equipo_visitante,
            fecha,
            fase,
            estadio,
            ciudad
        )

        if partido_actualizado is None:
            return error_respuesta("Partido no encontrado", 404) 

        return jsonify(partido_actualizado), 200

    except Exception as d:
           return error_respuesta(f"Error interno del servidor: {str(d)}", 500)



@app.route('/partidos/<int:id>', methods=['PATCH'])
def actualizar_partido_parcial(id):
    try:
        datos = request.get_json()

        if datos is None:
            return error_respuesta("Debes enviar un JSON", 400)

        if id <= 0:
            return error_respuesta("El id debe ser mayor que 0", 400)

        # Validar campos opcionales
        campos_validos = ["equipo_local", "equipo_visitante", "fecha", "fase", "estadio", "ciudad", "goles_local", "goles_visitante"]
        for campo in datos:
            if campo not in campos_validos:
                return error_respuesta(f"Campo no válido: {campo}", 400)

        # Validaciones básicas para campos proporcionados
        if "equipo_local" in datos:
            if not isinstance(datos["equipo_local"], str) or str(datos["equipo_local"]).strip() == "":
                return error_respuesta("El equipo local debe ser un texto no vacío", 400)
        if "equipo_visitante" in datos:
            if not isinstance(datos["equipo_visitante"], str) or str(datos["equipo_visitante"]).strip() == "":
                return error_respuesta("El equipo visitante debe ser un texto no vacío", 400)
        if "fase" in datos:
            if not isinstance(datos["fase"], str) or str(datos["fase"]).strip() == "":
                return error_respuesta("La fase debe ser un texto no vacío", 400)
        if "estadio" in datos:
            if not isinstance(datos["estadio"], str) or str(datos["estadio"]).strip() == "":
                return error_respuesta("El estadio debe ser un texto no vacío", 400)
        if "ciudad" in datos:
            if not isinstance(datos["ciudad"], str) or str(datos["ciudad"]).strip() == "":
                return error_respuesta("La ciudad debe ser un texto no vacío", 400)
        if "goles_local" in datos:
            try:
                int(datos["goles_local"])
            except:
                return error_respuesta("Los goles_local deben ser un número entero", 400)
        if "goles_visitante" in datos:
            try:
                int(datos["goles_visitante"])
            except:
                return error_respuesta("Los goles_visitante deben ser un número entero", 400)

        # Verificar que equipos no sean iguales si ambos están presentes
        equipo_local = datos.get("equipo_local", None)
        equipo_visitante = datos.get("equipo_visitante", None)
        if equipo_local and equipo_visitante and equipo_local.lower() == equipo_visitante.lower():
            return error_respuesta("El equipo local y el visitante no pueden ser iguales", 400)

        partido_actualizado = servicio_partidos.actualizar_partido_parcial(id, **datos)

        if partido_actualizado is None:
            return error_respuesta("Partido no encontrado", 404)

        return jsonify(partido_actualizado), 200

    except Exception as e:
        return error_respuesta(f"Error interno del servidor: {str(e)}", 500)

@app.route('/partidos/<int:id>', methods=['DELETE'])
def eliminar_partido(id):
    try:
        if id <= 0:
            return error_respuesta("El id debe ser mayor que 0", 400)

        eliminado = servicio_partidos.eliminar_partido(id)

        if not eliminado:
            return error_respuesta("Partido no encontrado", 404)

        return jsonify({"mensaje": "Partido eliminado exitosamente"}), 200

    except Exception as e:
        return error_respuesta(f"Error interno del servidor: {str(e)}", 500)

@app.route('/usuarios', methods=["POST"])
#crear usuarios
def crear_usuario():
    datos = request.get_json()
    if not datos:
        return jsonify({"Error": f"Por favor, proporcione los datos necesarios"}), 400
    campos_requeridos = ["nombre", "email"]
    for campo in campos_requeridos:
        if campo not in datos:
            return jsonify({"Error": f"Campo faltante ({campo})"}), 400
    
    try:
        #Obtiene datos del usuario
        nombre = datos.get("nombre")
        email = datos.get("email")

        #Crea un nuevo usuario y lo inserta en la tabla
        nuevo_usuario = servicios_usuarios.crear_usuario(nombre, email)
        return jsonify(nuevo_usuario), 201
    except Exception as e:
        return jsonify({"Error": str(e)}), 500

@app.route('/usuarios', methods=["GET"])
def mostrar_usuarios():
    #mostrar usuarios en la base de datos (soporta paginación)
    try:
        usuarios = servicios_usuarios.mostrar_usuarios()
        return jsonify(usuarios), 200
    except Exception as e:
        jsonify({f"Error: {str(e)}"}), 500
    
@app.route('/usuarios/<int:id>',methods=["GET"])
def obtener_usuario(id):
    try:
        if id<=0:
            return error_respuesta("ID de usuario invalido",400)
        
        usuario = servicios_usuarios.obtener_usuario_por_id(id)

        if usuario is None:
            return error_respuesta("El ID ingresado no fue encontrado o no existe", 404)
        
        return jsonify(usuario),200
    
    except Exception as e: 

        return error_respuesta(f"Error interno del servidor: {str(e)}", 500)  

@app.route('/usuarios/<int:id>',methods=["PUT"])
def editar_usuario(id):
    try:
        datos = request.get_json()
        
        if not datos:
            return error_respuesta("No se enviaron datos", 400)
        
        if id <= 0:
            return error_respuesta("ID de usuario invalido", 400)
            
        nombre = datos.get('nombre')
        email = datos.get('email')
        
        if not nombre or not email:
            return error_respuesta("Se deben completar todos los campos", 400)

        usuario_actualizado = servicios_usuarios.actualizar_usuario(id, nombre, email)
        
        if usuario_actualizado is None:
            return error_respuesta("Usuario no encontrado", 404)

        return jsonify(usuario_actualizado), 200

    except Exception as e:
        return error_respuesta(f"Error al actualizar: {str(e)}", 500)

#Eliminar usuario a través del ID
@app.route("/usuarios/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):
    try:
        usuario_eliminado = servicios_usuarios.eliminar_usuario(id)

        if not usuario_eliminado:
            return error_respuesta("Usuario no encontrado", 404)

        return jsonify({
            "mensaje":"Usuario eliminado correctamente", 
            "usuario": usuario_eliminado
        }), 200

    except ValueError as e:
        return error_respuesta(str(e), 400)

    except Exception as e:
        return error_respuesta(f"Error interno del servidor: {str(e)}", 500)


    
#POST PREDICCION
@app.route('/partidos/<int:id>/prediccion', methods=['POST'])
def crear_prediccion(id):
    try:
        # 1. Validar el ID de la URL
        if id <= 0:
            return error_respuesta("El id del partido debe ser mayor que 0", 400)

        datos = request.get_json()
        if not datos:
            return error_respuesta("Debes enviar un JSON", 400)

        # 2. Validar que vengan todos los campos necesarios
        campos_requeridos = ["id_usuario", "local", "visitante"]
        for campo in campos_requeridos:
            if campo not in datos:
                return error_respuesta(f"Falta el campo obligatorio {campo}", 400)

        # 3. Validar tipos de datos (que sean enteros mayores o iguales a 0)
        usuario_id = int(datos["id_usuario"])
        goles_local = int(datos["local"])
        goles_visitante = int(datos["visitante"])

        if goles_local < 0 or goles_visitante < 0 or usuario_id <= 0:
            return error_respuesta("Los goles no pueden ser negativos y el usuario_id debe ser mayor a 0", 400)

        # 4. Llamar al servicio para que se encargue de la lógica
        nueva_prediccion = servicio_partidos.crear_prediccion(id, usuario_id, goles_local, goles_visitante)

        return jsonify({
            "mensaje": "Predicción creada exitosamente",
            "prediccion": nueva_prediccion
        }), 201

    except ValueError:
        return error_respuesta("Los valores enviados deben ser números", 400)
    except Exception as e:
        # Atrapamos errores específicos de la base de datos (Ej: partido/usuario no existe, o predicción duplicada)
        if "DUPLICADA" in str(e):
            return error_respuesta("El usuario ya tiene una predicción para este partido", 409)
        elif "NO ENCONTRADO" in str(e):
            return error_respuesta(str(e), 404)
        elif "PARTIDO_JUGADO" in str(e):
            return error_respuesta("El partido ya fue jugado, no se permiten predicciones", 400)
        
        return error_respuesta("Error interno del servidor", 500)

@app.route('/ranking', methods=['GET'])
def obtener_ranking():
    try:
        _limit = request.args.get('_limit', type=int) 
        _offset = request.args.get('_offset', default=0, type=int)

        if _limit is not None and _limit <= 0:
            return jsonify({
                "errors": [{
                    "code": "BAD_REQUEST",
                    "message": "Límite inválido",
                    "level": "error",
                    "description": "El límite (_limit) debe ser un número mayor a 0."
                }]
            }), 400

        if _offset < 0:
            return jsonify({
                "errors": [{
                    "code": "BAD_REQUEST",
                    "message": "Offset inválido",
                    "level": "error",
                    "description": "El desplazamiento (_offset) no puede ser negativo."
                }]
            }), 400

        ranking = servicios_usuarios.obtener_ranking()
        
        if not ranking and _offset == 0:
            return '', 204

        total = len(ranking)
        
        # Paginación manual en la lista
        if _limit is not None:
            ranking_paginado = ranking[_offset : _offset + _limit]
        else:
            ranking_paginado = ranking[_offset:]

        links = {}
        if _limit is not None:
            from urllib.parse import urlencode
            args = request.args.copy()
            url_base = request.base_url

            def construir_url(offset_val):
                args_copy = args.copy()
                args_copy['_offset'] = offset_val
                args_copy['_limit'] = _limit
                return f"{url_base}?{urlencode(args_copy)}"

            last_page_offset = max(0, (total - 1) // _limit * _limit) if total > 0 else 0

            links = {
                '_first': {"href": construir_url(0)},
                '_last': {"href": construir_url(last_page_offset)}
            }

            if _offset > 0:
                links['_prev'] = {"href": construir_url(max(0, _offset - _limit))}

            if _offset + _limit < total:
                links['_next'] = {"href": construir_url(_offset + _limit)}

            return jsonify({
                'ranking': ranking_paginado,
                '_links': links
            }), 200

        return jsonify({
            'ranking': ranking_paginado
        }), 200

    except Exception as e:
        return jsonify({
            "errors": [{
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Error interno del servidor",
                "level": "error",
                "description": str(e)
            }]
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
