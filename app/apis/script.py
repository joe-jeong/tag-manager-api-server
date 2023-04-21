from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config.container_config import BUCKET_NAME
from app.utils import container_util, s3_util
from app.model.models import User, Container, Script
import os
import uuid
from flask_restx import Namespace, Resource

bp = Blueprint('script', __name__, url_prefix='/script')
ns = Namespace(name='script',
               description='스크립트 관련 API'
               )

@ns.route("/<int:container_id>/list")
class ScriptsOfContainer(Resource):
    @jwt_required()
    def get(self, container_id):
        """container_id와 일치하는 컨테이너의 스크립트 정보 리스트를 반환합니다."""
        response = dict()
        scripts = Container.get(container_id).scripts

        for script in scripts:
            response[script.id] = {"name": script.name, "description": script.description}
        
        return response, 200


@ns.route("")
class ScriptCreate(Resource):
    @jwt_required()
    def post(self):
        """새로운 스크립트를 생성합니다."""
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
        s3_path = f"script/{filename}"
        s3_client.upload_file(path, BUCKET_NAME, s3_path)    
        s3_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{s3_path}"

        os.remove(path)

        Script.save(name=name, description=desc, s3_path=s3_path, file_url=s3_url, container_id=container_id) 

        return {'msg':'success'}, 200