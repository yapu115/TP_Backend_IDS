from flask import Flask, jsonify, request
from services import servicio_partidos
from utils.errores import error_respuesta

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '¡Hola, mundo! El servidor Flask está funcionando.'

@app.route('/partidos', methods=['GET'])
def obtener_partidos():
    partidos = servicio_partidos.obtener_todos_los_partidos()
    
    respuesta_json = [partido.to_dict() for partido in partidos]

    return jsonify(respuesta_json)

#PUT DE RESULTADOS
@app.route('/partidos/<int:id>/resultado', methods=["PUT"])
def actualizar_resultado(id):
    try:

        datos = request.get_json()

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

        equipo_local = datos["equipo_local"].str()
        equipo_visitante = datos["equipo_visitante"].str()
        fecha = datos["fecha"].str()
        fase = datos["fase"].str()
        estadio = datos["estadio"].str()
        ciudad = datos["ciudad"].str()

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


if __name__ == '__main__':
    app.run(debug=True)
