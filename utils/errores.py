from flask import jsonify

def error_respuesta(mensaje, codigo):
    return jsonify({"error" : mensaje}), codigo