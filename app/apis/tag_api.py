from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

from app.model.medium import Medium, PlatformList
from app.model.tag import Tag
from flask_restx import Namespace, Resource, fields, reqparse

ns = Namespace(
    name='tag',
    description='태그 관련 API'
)

class _Schema():
    param_list = ns.model('json 타입의 파라미터 리스트', {
        'parameter name': fields.String(description='parameter value', example='123121')
    })

    post_fields = ns.model('태그 생성 시 필요 데이터', {
        "name": fields.String(description='Tag name', example='Test-Tag-1'),
        "param": fields.Nested(param_list),
        'script': fields.String(description='tag script js code', example="(event)=>{gtag('event', 'submit');}"),
        'event_id': fields.Integer(description='Event ID of the tag', example=1),
        "medium_id": fields.Integer(description='Medium ID of the tag', example=1)
    })

    put_fields = ns.model('태그 수정 시 필요 데이터', {
        "name": fields.String(description='Tag name', example='Test-Tag-1'),
        "param": fields.Nested(param_list),
        'script': fields.String(description='tag script js code', example="(event)=>{gtag('event', 'submit');}")
    })


    basic_fields = ns.inherit('태그 기본정보', put_fields,{
        'id': fields.Integer(description='event id', example=1),
        "name": fields.String(description='Tag name', example='Test-Tag-1'),
    })

    detail_fields = ns.inherit('태그 상세정보', basic_fields, {
        'event_id': fields.Integer(description='Event_id of tage', example=1),
        "medium_id": fields.Integer(description='Medium ID of the tag', example=1)
    })

    tag_list = fields.List(fields.Nested(basic_fields))

    msg_fields = ns.model('상태 코드에 따른 설명', {
        'msg': fields.String(description='상태 코드에 대한 메세지', example='ok')
    })
    

@ns.route('')
class GetTagOrCreate(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('container_name', type=str, help="컨테이너 이름")
    parser.add_argument('event_name', type=str, help="이벤트 id")
    parser.add_argument('medium_name', type=str, help="매체 id")
    
    @ns.response(200, '태그 조회 성공', _Schema.tag_list)
    @ns.doc(params={'container_name': {'description': '컨테이너 이름', 'in': 'query', 'type': 'string'},
                    'event_name': {'description': '이벤트 이름', 'in': 'query', 'type': 'string'},
                    'medium_name': {'description': '매체 이름', 'in': 'query', 'type': 'string'},})
    def get(self):
        """선택한 매체와 이벤트에 연결된 태그를 조회합니다."""
        args = self.parser.parse_args()
        tag = Tag.get_by_event_and_medium(args['container_name'], args['event_name'], args['medium_name'])
        response = {
                "id": tag.id,
                "name": tag.name,
                "param": tag.param,
                "script": tag.script
            }
            
        return response, 200


    @ns.expect(_Schema.post_fields)
    @ns.response(201, '태그 생성 성공')
    def post(self):
        """선택한 매체와 이벤트에 연결되는 태그를 생성합니다"""
        body = request.json
        name = body['name']
        event_id = body['event_id']
        medium_id = body['medium_id']
        param = body['param']
        script = body['script']

        Tag.save(event_id, medium_id, name, param, script)

        return {'msg':'ok'}, 201


@ns.route('/<string:tag_name>')
@ns.doc(params={'tag_name': "태그 이름"})
class TagManage(Resource):

    @ns.response(200, '태그 정보 조회 성공', _Schema.basic_fields)
    def get(self, tag_name):
        """tag_name와 일치하는 태그의 상세정보를 가져옵니다"""
        tag = Tag.get_by_name(tag_name)
        response = {
                "id": tag.id,
                "name": tag.name,
                "param": tag.param,
                "script": tag.script,
                "event_id": tag.event_id,
                "medium_id": tag.medium_id
            }

        return response, 200
    

    @ns.expect(200, "새로운 태그 데이터", _Schema.put_fields)
    @ns.response(200, "태그 데이터 수정 성공", _Schema.msg_fields)
    def put(self, tag_name):
        """medium_name와 일치하는 매체의 tracking_id 데이터를 수정합니다"""
        body = request.json
        tag = Tag.get_by_name(tag_name)
        tag.update(body['name'], body['param'], body['script'])
        return {"msg": "ok"}, 200

    
    @ns.response(200, "태그 데이터 삭제 성공", _Schema.msg_fields)
    def delete(self, tag_name):
        """medium_name와 일치하는 매체 엔티티를 삭제합니다"""
        Tag.delete(tag_name)
        return {"msg": "ok"}, 200