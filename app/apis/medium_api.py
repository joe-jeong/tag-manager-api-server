from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

from app.model.medium import Medium, PlatformList
from app.model.container import Container
from flask_restx import Namespace, Resource, fields, reqparse

ns = Namespace(
    name='medium',
    description='매체 관련 API'
)

class _Schema():
    tracking_list = ns.model('json 타입의 트래킹 id 리스트', {
        'alias of tracking id': fields.String(description='tracking id', example="G1231343")
    })

    platform_fields = ns.model('플렛폼 기본 정보', {
        'id': fields.Integer(description = "Platform ID", example=1),
        'name': fields.String(description = "Platform name", example='Google Analytics')
    })

    post_fields = ns.model('매체 생성 시 필요 데이터', {
        'platform_id': fields.Integer(description = "Medium ID in medium list", example=1),
        'name': fields.String(description='medium name', example="GA-for-tracking-behavior"),
        'container_id': fields.Integer(description="Container ID of the medium", example=1),
        'tracking_list': fields.Nested(tracking_list)
    })

    put_fields = ns.model('매체 수정 시 필요 데이터', {
        'name': fields.String(description='medium name', example="GA-for-tracking-behavior"),
        'tracking_list': fields.Nested(tracking_list)
    })

    basic_fields = ns.model('매체 기본정보', {
        'platform_id': fields.Integer(description='platform id', example=1),
        'platform_name': fields.String(description='platform name', example='GA'),
        'id': fields.Integer(description='Medium ID', example=1),
        'name': fields.String(description='medium name', example="GA-for-tracking-behavior"),
        'is_using': fields.Boolean(description='Whether or not the medium is running', example=1)
    })

    medium_list = fields.List(fields.Nested(basic_fields))

    platform_list = fields.List(fields.Nested(platform_fields))

    detail_fields = ns.inherit('매체 상세정보', basic_fields, {
        'container_id': fields.Integer(description='container_id', example=1),
        'tracking_list': fields.Nested(tracking_list)
    })

    msg_fields = ns.model('상태 코드에 따른 설명', {
        'msg': fields.String(description='상태 코드에 대한 메세지', example='ok')
    })
    

@ns.route('/platform-list')
class GetPlatformList(Resource):
    @ns.response(200, '매체 플랫폼 리스트 조회 성공', _Schema.platform_list)
    def get(self):
        """서비스에서 사용가능한 플랫폼 리스트를 가져옵니다."""
        platforms = PlatformList.get_all()
        response = [
            {
            "id": platform.id,
            "name": platform.name
            }
            for platform in platforms
        ]
        
        return response, 200



@ns.route('/list')
@ns.doc(params={'container_name': {'description': '컨테이너 이름', 'in': 'query', 'type': 'string'}})
class MediumList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('container_name', type=str, help="컨테이너의 이름")

    @ns.response(200, '매체 리스트 조회 성공', _Schema.medium_list)
    def get(self):
        """현재 컨테이너의 매체 리스트를 가져옵니다."""
        args = self.parser.parse_args()
        print(args['container_name'])
        mediums = Container.get_mediums(args['container_name'])
        print(args['container_name'])
        response = [
            {
                "platform_id": medium.platform_id,
                'platform_name': PlatformList.get_name(medium.platform_id),
                "id": medium.id,
                "name": medium.name,
                "is_using": medium.is_using
            }
            for medium in mediums
        ]
        return response, 200
    

@ns.route('')
class MediumCreate(Resource):
    @ns.expect(_Schema.post_fields)
    @ns.response(201, '컨테이너에 매체 추가 성공', _Schema.msg_fields)
    def post(self):
        """현재 컨테이너에 매체 정보를 추가합니다"""
        body = request.json
        container_id = body['container_id']
        platform_id = body['platform_id']
        name = body['name']
        tracking_list = body['tracking_list']

        Medium.save(container_id, name, platform_id, tracking_list)

        return {'msg':'ok'}, 201


@ns.route('/<string:medium_name>')
@ns.doc(params={'medium_name': '매체 이름'})
class MediumManage(Resource):

    @ns.response(200, "매체 정보 조회 성공", _Schema.detail_fields)
    def get(self, medium_name):
        """medium_id와 일치하는 매체의 상세정보를 가져옵니다"""
        medium = Medium.get_by_name(medium_name)
        response = {
            "id": medium.id,
            "name": medium.name,
            "is_using": medium.is_using,
            "tracking_list": medium.tracking_list,
            "container_id": medium.container_id,
            "platform_id": medium.platform_id,
            "tracking_list": medium.tracking_list
        }
        return response, 200
    
    @ns.expect(200, "새로운 매체 데이터", _Schema.put_fields)
    @ns.response(200, "매체 tracking_list 수정 성공", _Schema.msg_fields)
    def put(self, medium_name):
        """medium_id와 일치하는 매체의 tracking_id 데이터를 수정합니다"""
        body = request.json
        name = body['name']
        tracking_list = body['tracking_list']
        medium = Medium.get(medium_name)
        medium.update_name_tracking_list(name, tracking_list)
        return {"msg": "ok"}, 200
    
    @ns.response(200, "매체 데이터 삭제 성공", _Schema.msg_fields)
    def delete(self, medium_name):
        """medium_id와 일치하는 매체 엔티티를 삭제합니다"""
        Medium.delete(medium_name)
        return {"msg": "ok"}, 200

