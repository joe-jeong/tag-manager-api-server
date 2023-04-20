from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config.container_config import BUCKET_NAME
from app.utils import container_util, s3_util
from app.model.models import User, Container, Script
import os
import uuid

bp = Blueprint('script', __name__, url_prefix='/script')

@bp.route("<int:container_id>/list", methods=['GET'])
@jwt_required()
def get_scripts(container_id):
    response = dict()
    scripts = Container.get(container_id).scripts

    for script in scripts:
        response[script.id] = {"name": script.name, "description": script.description}
    
    return jsonify(response)

@bp.route("", methods=['POST'])
@jwt_required()
def create_script():
    data = request.json
    name = data['name']
    desc = data['description']
    code = data['code']
    container_id = data['container_id']
    filename = str(uuid.uuid4()) + '.js'
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path, 'w') as f:
        f.write(code)

    s3_client = s3_util.s3_connection()
    s3_filename = f"script/{filename}"
    s3_client.upload_file(path, BUCKET_NAME, s3_filename)    
    s3_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/script/{filename}"

    os.remove(path)

    Script.save(name=name, description=desc, file_name=s3_filename, file_path=s3_url, container_id=container_id) 

    return jsonify(messege="success!"), 200