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
        '트래킹id 별칭': fields.Integer(description='트래킹 id')
    })

    post_fields = ns.model('매체 생성/수정 시 필요 데이터', {
        'platform_id': fields.Integer(description = "Medium ID in medium list"),
        'container_id': fields.Integer(description="Container ID of the medium"),
        'tracking_list': fields.Nested(tracking_list)
    })

    basic_fields = ns.model('매체 기본정보', {
        'platform_id': fields.Integer(description='platform id'),
        'platform_name': fields.String(description='platform name'),
        'id': fields.Integer(description='Medium ID'),
        'is_using': fields.Boolean(description='Whether or not the medium is running')
    })

    medium_list = fields.List(fields.Nested(basic_fields))

    detail_fields = ns.inherit('매체 상세정보', basic_fields, {
        'container_id': fields.Integer(description='container_id'),
        'tracking_list': fields.Nested(tracking_list)
    })

    msg_fields = ns.model('상태 코드에 따른 설명', {
        'msg': fields.String(description='상태 코드에 대한 메세지')
    })
    

@ns.route('/platform-list')
class GetPlatformList(Resource):
    @ns.response(200, '매체 플랫폼 리스트 조회 성공', _Schema.medium_list)
    def get(self):
        """서비스에서 사용가능한 플랫폼 리스트를 가져옵니다."""
        platforms = PlatformList.get_all()
        response = [{
            "id": platform.id,
            "name": platform.name}
            for platform in platforms]
        
        return response, 200



@ns.route('/list')
@ns.doc(params={'container_id': {'description': '컨테이너 id', 'in': 'query', 'type': 'int'}})
class MediumList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('container_id', type=int, help="컨테이너의 id")
    @ns.response(200, '매체 리스트 조회 성공', _Schema.medium_list)
    def get(self):
        """현재 컨테이너의 매체 리스트를 가져옵니다."""
        args = self.parser.parse_args()
        mediums = Container.get_mediums(args['container_id'])
        response = [
            {
            "platform_id": medium.platform_id,
            'platform_name': PlatformList.get_name(medium.platform_id),
            "id": medium.id,
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
        tracking_list = body['tracking_list']

        Medium.save(container_id, platform_id, tracking_list)

        return {'msg':'ok'}, 201


@ns.route('/<int:medium_id>')
@ns.doc(params={'medium_id': '매체 id'})
class MediumManage(Resource):

    @ns.response(200, "매체 정보 조회 성공", _Schema.detail_fields)
    def get(self, medium_id):
        """medium_id와 일치하는 매체의 상세정보를 가져옵니다"""
        medium = Medium.get(medium_id)
        response = {
            "id": medium.id,
            "is_using": medium.is_using,
            "tracking_list": medium.tracking_list,
            "container_id": medium.container_id,
            "platform_id": medium.platform_id,
            "tracking_list": medium.tracking_list
        }
        return response, 200
    
    @ns.expect(200, "새로운 매체 데이터", _Schema.post_fields)
    @ns.response(200, "매체 tracking_list 수정 성공", _Schema.msg_fields)
    def put(self, medium_id):
        """medium_id와 일치하는 매체의 tracking_id 데이터를 수정합니다"""
        tracking_list = request.json
        medium = Medium.get(medium_id)
        medium.update_tracking_list(tracking_list)
        return {"msg": "ok"}, 200
    
    @ns.response(200, "매체 데이터 삭제 성공", _Schema.msg_fields)
    def delete(self, medium_id):
        """medium_id와 일치하는 매체 데이터를 삭제합니다"""
        Medium.delete(medium_id)
        return {"msg": "ok"}, 200

