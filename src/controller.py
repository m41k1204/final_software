# src/controller.py
from flask import Flask, jsonify, request

from data_handler import DataHandler
from models.usuario import Usuario
from models.asignacion import Asignacion
from models.tarea import Tarea

app = Flask(__name__)
data_handler = DataHandler()

@app.route("/dummy", methods=["GET"])
def dummy():
    return jsonify({"message": "This is a dummy endpoint!"})


@app.route("/usuarios", methods=["POST"])
def create_user():
    body = request.get_json(silent=True) or {}
    missing = [f for f in ("id", "name", "email") if f not in body]
    if missing:
        return jsonify({"error": f"Faltan parametros: {', '.join(missing)}"}), 400

    try:
        new_user = Usuario(body["id"], body["name"], body["email"])
        data_handler.add_user(new_user)
        return jsonify(new_user.to_dict()), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409


@app.route("/usuarios", methods=["GET"])
def list_users():
    return jsonify([u.to_dict() for u in data_handler.get_users()])

@app.route("/usuarios", methods=["GET"])
def get_usuario_por_alias():
    alias = request.args.get("mialias")          

    if not alias:
        return jsonify({"error": "'mialias' is esperado"}), 400

    user = data_handler.find_user_by_email(alias)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(user.to_dict()) 

@app.route("/tasks", methods=["POST"])
def create_task():
    body = request.get_json(silent=True) or {}
    required = ["nombre", "descripcion", "usuario", "rol"]
    missing  = [k for k in required if k not in body]
    if missing:
        return jsonify({"error": f"Faltan campos: {', '.join(missing)}"}), 400

    user = data_handler.find_user_by_email(body["usuario"])
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    try:
        asignacion = Asignacion(user.email, body["rol"].lower())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    tarea = Tarea(body["nombre"], body["descripcion"])
    tarea.add_asignacion(asignacion)

    data_handler.add_task(tarea)
    return jsonify(tarea.to_dict()), 201

@app.route("/tasks/<task_id>", methods=["POST"])
def update_task_state(task_id):
    tarea = data_handler.find_task_by_id(task_id)
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404

    body  = request.get_json(silent=True) or {}
    nuevo = body.get("estado")
    if not nuevo:
        return jsonify({"error": "Campo 'estado' requerido"}), 400

    try:
        tarea.set_estado(nuevo.lower())
        data_handler._save()
        return jsonify(tarea.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@app.route("/tasks/<task_id>/users", methods=["POST"])
def task_users(task_id):
    tarea = data_handler.find_task_by_id(task_id)
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404

    body = request.get_json(silent=True) or {}
    alias  = body.get("usuario")
    rol    = body.get("rol", "").lower()
    accion = body.get("accion", "").lower()

    if not alias or accion not in {"adicionar", "remover"}:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    usuario = data_handler.find_user_by_email(alias)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    try:
        if accion == "adicionar":
            if any(a.usuario_alias == alias for a in tarea.asignaciones):
                raise ValueError("Usuario ya esta asignado a la tarea")
            asignacion = Asignacion(alias, rol)
            tarea.add_asignacion(asignacion)

        else:  
            if not any(a.usuario_alias == alias for a in tarea.asignaciones):
                raise ValueError("Usuario no asignado a la tarea")
            tarea.remove_asignacion(alias)

        data_handler._save()
        return jsonify(tarea.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

@app.route("/tasks/<task_id>/dependencies", methods=["POST"])
def task_dependencies(task_id):
    tarea = data_handler.find_task_by_id(task_id)
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404

    body  = request.get_json(silent=True) or {}
    dep_id = body.get("dependencytaskid")
    accion = body.get("accion", "").lower()

    if not dep_id or accion not in {"adicionar", "remover"}:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    dep_task = data_handler.find_task_by_id(dep_id)
    if not dep_task:
        return jsonify({"error": "Tarea de dependencia no encontrada"}), 404

    try:
        if accion == "adicionar":
            tarea.add_dependency(dep_id)
        else:
            tarea.remove_dependency(dep_id)

        data_handler._save()
        return jsonify(tarea.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


if __name__ == "__main__":
    app.run(debug=True)
