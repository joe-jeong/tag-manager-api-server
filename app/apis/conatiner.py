from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config.container_config import BUCKET_NAME
from app.utils import container_util, s3_util
from app.model.models import User, Container, Script
import os
import uuid

bp = Blueprint('container', __name__, url_prefix='/container')

@bp.route("/list", methods=['GET'])
@jwt_required()
def get_containers():
    response = dict()
    containers = User.get_containers(get_jwt_identity())

    for container in containers:
        response[container.id] = {"name": container.name, "description": container.description}
    
    return jsonify(response)

@bp.route("", methods=['POST'])
@jwt_required()
def create_container():
    data = request.json
    name = data['name']
    desc = data['description']
    filename = str(uuid.uuid4()) + '.js'
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    container = Container.save_empty_entity(get_jwt_identity())
    tag = container_util.get_container_tag(container.id)
    with open(path, 'w') as f:
        f.write(tag)

    s3_client = s3_util.s3_connection()
    s3_filename = f"container_tag/{filename}"
    s3_client.upload_file(path, BUCKET_NAME, s3_filename)    
    s3_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/container_tag/{filename}"

    os.remove(path)

    container.update(name=name, description=desc, file_name=s3_filename, file_path=s3_url) 

    return jsonify({'container_tag': tag})


@bp.route('/<int:container_id>', methods=['GET'])
@jwt_required()
def get_container(container_id):
    print(container_id)
    container = Container.get(container_id)
    response = {
        "id" : container.id,
        "name" : container.name,
        "description" : container.description,
        "file_name" : container.file_name,
        "file_path" : container.file_path
    }

    return jsonify(response)


@bp.route("/<int:container_id>", methods=["PUT"])
@jwt_required()
def update_container(container_id):
    data = request.json
    name = data['name']
    desc = data['description']

    Container.update_info(container_id, name, desc)

    return jsonify({"status": "ok"}), 200

@bp.route("/<int:container_id>", methods=["DELETE"])
@jwt_required()
def remove_container(container_id):
    user_id = get_jwt_identity()
    key = Container.get(container_id).file_name
    s3_client = s3_util.s3_connection()
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
    Container.delete(user_id, container_id)

    
    return jsonify({"status": "ok"}), 200

@bp.route("/<int:container_id>/scripts")
def get_scripts(container_id):
    res = []
    scripts = Container.get(container_id).scripts
    for script in scripts:
        res.append(script.file_path)
    return jsonify(res), 200
