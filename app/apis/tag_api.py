from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

from app.model.medium import Medium, PlatformList
from app.model.tag import Tag
from flask_restx import Namespace, Resource, fields, reqparse

ns = Namespace(
    name='tag',
    description='태그 관련 API',
    path='/'
)

class _Schema():

    post_fields = ns.model('태그 생성 시 필요 데이터', {
        "name": fields.String(description='Tag name', example='tag1'),
        'script': fields.String(description='tag script js code', example="(event)=>{gtag('event', 'submit');}")
    })

    basic_fields = ns.model('태그 수정/조회 시 필요 데이터', {
        "name": fields.String(description='Tag name', example='tag1'),
        'script': fields.String(description='tag script js code', example="(event)=>{gtag('event', 'submit');}")
    })

    tag_list = fields.List(fields.Nested(basic_fields))

    msg_fields = ns.model('상태 코드에 따른 설명', {
        'msg': fields.String(description='상태 코드에 대한 메세지', example='처리 내용')
    })
    

@ns.route('/containers/<string:container_domain>/tags')
@ns.doc(params={'platform_name': {'description': '플랫폼 이름', 'in': 'query', 'type': 'string'},
                'event_name': {'description': '이벤트 이름', 'in': 'query', 'type': 'string'},})
class GetTagOrCreate(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('platform_name', type=str, help="플랫폼 이름")
    parser.add_argument('event_name', type=str, help="이벤트 이름")
    
    @ns.response(200, '태그 조회 성공', _Schema.tag_list)
    @ns.response(400, '태그 조회 실패', _Schema.msg_fields)
    def get(self, container_domain):
        """선택한 매체와 이벤트에 연결된 태그를 조회합니다."""
        args = self.parser.parse_args()
        tag = Tag.get_by_event_and_medium(container_domain, args['platform_name'], args['event_name'])
        
        if not tag:
            return {'msg':'해당 플랫폼과 이벤트에 연결된 태그가 존재하지 않습니다'}, 404
        
        response = {
                "name": tag.name,
                "script": tag.script
            }
        return response, 200


    @ns.expect(_Schema.post_fields)
    @ns.response(200, '태그 생성/수정 성공', _Schema.msg_fields)
    @ns.response(400, '태그 생성/수정 실패', _Schema.msg_fields)
    def post(self, container_domain):
        """선택한 매체와 이벤트에 연결되는 태그를 생성/수정합니다"""
        args = self.parser.parse_args()
        body = request.json
        name = body['name']
        event_name = args['event_name']
        platform_name = args['platform_name']
        script = body['script']

        tag = Tag.save(container_domain, event_name, platform_name, name, script)

        if not tag:
            return {'msg':'컨테이너 내에 동일한 이름의 태그가 이미 존재합니다.'}, 400
        
        return {'msg':'ok'}, 200


@ns.route('/containers/<string:container_domain>/tags/<string:tag_name>')
@ns.doc(params={'tag_name': "태그 이름"})
class TagManage(Resource):

    @ns.response(200, '태그 정보 조회 성공', _Schema.basic_fields)
    def get(self, container_domain, tag_name):
        """tag_name와 일치하는 태그의 상세정보를 가져옵니다"""
        tag = Tag.get_by_container_and_name(container_domain, tag_name)
        response = {
                "name": tag.name,
                "script": tag.script
            }
        return response, 200
    
    
    @ns.response(200, "태그 데이터 삭제 성공", _Schema.msg_fields)
    def delete(self, tag_name):
        """medium_name와 일치하는 매체 엔티티를 삭제합니다"""
        Tag.delete(tag_name)
        return {"msg": "ok"}, 200