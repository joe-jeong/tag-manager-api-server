from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config.container_config import BUCKET_NAME
from app.utils import container_util, s3_util
from app.model.models import User, Container, Script
import os
import uuid
from flask_restx import Namespace, Resource, fields

bp = Blueprint('container', __name__, url_prefix='/container')
ns = Namespace(
    name='container',
    description='컨테이너 관련 API'
    )

class Schema():
    post_fields = ns.model('컨테이너 생성시 필요 데이터', {
        'name': fields.String(description='Container Name'),
        'description': fields.String(description='Container Description')
    })

    basic_fields = ns.inherit('컨테이너 기본 정보', post_fields, {
        'id': fields.Integer(description='Container ID'),
    })

    detail_fields = ns.inherit('컨테이너 상세 정보', basic_fields, {
        's3_path': fields.String(description='S3 storage path of the file'),
        'file_url': fields.String(description='URL where the file is saved')
    })

    file_url_fields = ns.model('파일 저장 url',{

    })

    container_list = fields.List(fields.Nested(basic_fields))
    url_list = fields.List(fields.String, description='스크립트가 저장된 s3 url')


@ns.route('/list')
class ContainerList(Resource):
    @jwt_required()
    @ns.response(200, 'Success', Schema.container_list)
    def get(self):
        """현재 회원의 컨테이너 리스트를 가져옵니다."""
        response = list()
        containers = User.get_containers(get_jwt_identity())

        for container in containers:
            response.append(
                {"id": container.id, "name": container.name, "description": container.description}
            )
        
        return response, 200


@ns.route('')
class ContainerCreate(Resource):
    @jwt_required()
    @ns.expect(Schema.post_fields)
    @ns.doc(responses={200: '컨테이너 생성 성공'})
    def post(self):
        """새 컨테이너를 추가합니다."""
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
        s3_path = f"container_tag/{filename}"
        s3_client.upload_file(path, BUCKET_NAME, s3_path)    
        s3_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{s3_path}"

        os.remove(path)

        container.update(name=name, description=desc, s3_path=s3_path, file_url=s3_url) 

        return {'msg':'ok'}, 201
    

@ns.route('/<int:container_id>')
@ns.doc(params={'container_id': '컨테이너의 id'})
class ContainerManage(Resource):
    @jwt_required()
    @ns.doc(responses={200: '컨테이너 조회 성공'})
    @ns.response(200, "컨테이너 정보 조회 성공", Schema.detail_fields)
    def get(self, container_id):
        """container_id와 일치하는 컨테이너의 상세 정보를 가져옵니다."""
        print(container_id)
        print(type(container_id))
        container = Container.get(container_id)
        response = {
            "id" : container.id,
            "name" : container.name,
            "description" : container.description,
            "s3_path" : container.s3_path,
            "file_url" : container.file_url
        }

        return response, 200


    @jwt_required()
    @ns.expect(200, "컨테이너 정보 수정 성공", Schema.post_fields)
    @ns.doc(responses={200:"컨테이너 정보 수정 성공"})
    def put(self, container_id):
        """container_id와 일치하는 컨테이너의 정보를 수정합니다."""
        data = request.json
        name = data['name']
        desc = data['description']

        Container.update_info(container_id, name, desc)

        return jsonify({"status": "ok"}), 200

    @jwt_required()
    @ns.doc(responses={200:"컨테이너 삭제 성공"})
    def delete(self, container_id):
        """container_id와 일치하는 컨테이너를 삭제합니다."""
        user_id = get_jwt_identity()
        key = Container.get(container_id).s3_path
        s3_client = s3_util.s3_connection()
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
        Container.delete(user_id, container_id)

        return jsonify({"status": "ok"}), 200


@ns.route('/<int:container_id>/scripts')
@ns.doc(params={'container_id': '컨테이너의 id'})
class ScriptsOfContainer(Resource):
    @ns.response(200, 'Success', Schema.url_list)
    def get(self, container_id):
        """container_id와 일치하는 컨테이너의 script들이 저장된 url 리스트를 반환합니다."""
        res = []
        scripts = Container.get(container_id).scripts
        for script in scripts:
            res.append(script.file_url)
        return res, 200
