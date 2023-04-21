from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config.container_config import BUCKET_NAME
from app.utils import container_util, s3_util
from app.model.models import User, Container, Script
import os
import uuid
from flask_restx import Namespace, Resource, fields

ns = Namespace(name='script',
               description='스크립트 관련 API'
               )


class _Schema():
    post_fields = ns.model('스크립트 생성시 필요 데이터', {
        'name': fields.String(description='Script Name'),
        'description': fields.String(description='Script Description'),
        'code': fields.String(description='script code'),
        'container_id': fields.Integer(description='container_id')
    })

    basic_fields = ns.model('스크립트 기본 정보', {
        'id': fields.Integer(description='Script ID'),
        'name': fields.String(description='Script Name'),
        'description': fields.String(description='Script Description')
    })

    detail_fields = ns.inherit('스크립트 상세 정보', basic_fields, {
        'code': fields.String(description='script code'),
        'container_id': fields.Integer(description='container_id')
    })

    msg_fields = ns.model('상태 코드에 따른 설명', {
        'msg': fields.String(description='상태 코드에 대한 메세지')
    })

    script_list = fields.List(fields.Nested(basic_fields))


@ns.route("/<int:container_id>/list")
@ns.doc(params={'container_id': '컨테이너의 id'})
class ScriptsOfContainer(Resource):
    @jwt_required()
    @ns.response(200, '스크립트 리스트 조회 성공', _Schema.script_list)
    def get(self, container_id):
        """container_id와 일치하는 컨테이너의 스크립트 정보 리스트를 반환합니다."""
        response = list()
        scripts = Container.get(container_id).scripts

        for script in scripts:
           response.append({"id": script.id, "name": script.name, "description": script.description})
        
        return response, 200


@ns.route("")
class ScriptCreate(Resource):
    @jwt_required()
    @ns.expect(_Schema.post_fields)
    @ns.response(201, "스크립트 생성 성공", _Schema.msg_fields)
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

        return {'msg':'success'}, 201
    
@ns.route("/<int:script_id>")
@ns.doc(params={'script_id': '스크립트의 id'})
class ScriptManage(Resource):
    @jwt_required()
    @ns.response(200, "스크립트 정보 조회 성공", _Schema.detail_fields)
    def get(self, script_id):
        """스크립트의 상세 정보를 가져옵니다."""
        script = Script.get(script_id)
        s3_resource = s3_util.s3_resource()
        script_file = s3_resource.Object(BUCKET_NAME, script.s3_path)
        code = script_file.get()['Body'].read().decode('utf-8')

        response = {
            "id" : script.id,
            "name" : script.name,
            "description" : script.description,
            "container_id": script.container.id,
            "code": code
        }

        return response, 200