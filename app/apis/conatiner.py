from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config.container_config import CONTAINER_TAG_TEMPLATE, BUCKET_NAME
from app.utils import s3
from app.model.models import User, Container
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

@bp.route("", methods=['POST'])
@jwt_required()
def create_container():
    data = request.json
    name = data['name']
    desc = data['description']
    tag = CONTAINER_TAG_TEMPLATE
    filename = str(uuid.uuid4()) + '.js'
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path, 'w') as f:
        f.write(tag)

    s3_client = s3.s3_connection()
    s3_client.upload_file(path, BUCKET_NAME, 'container_tag/' + filename)    
    s3_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/container_tag/{filename}"

    os.remove(path)

    Container.save(name=name, description=desc, file_name= filename, file_path=s3_url, user_id=get_jwt_identity()) 

    return jsonify({'container_tag': tag})

