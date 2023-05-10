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
        '파라미터 이름': fields.String(description='파라미터 값')
    })

    post_fields = ns.model('태그 생성 시 필요 데이터', {
        "param": fields.Nested(param_list),
        'script': fields.String(description='tag script js code'),
        'event_id': fields.Integer(description='Event ID of the tag'),
        "medium_id": fields.Integer(description='Medium ID of the tag')
    })

    put_fields = ns.model('태그 수정 시 필요 데이터', {
        "param": fields.Nested(param_list),
        'script': fields.String(description='tag script js code')
    })


    basic_fields = ns.model('태그 기본정보', {
        'id': fields.Integer(description='event id'),
        "param": fields.Nested(param_list),
        'script': fields.String(description='tag script js code')
    })

    detail_fields = ns.inherit('태그 상세정보', {
        'event_id': fields.Integer(description='Event_id of tage'),
        "medium_id": fields.Integer(description='Medium ID of the tag')
    })

    tag_list = fields.List(fields.Nested(basic_fields))

    msg_fields = ns.model('상태 코드에 따른 설명', {
        'msg': fields.String(description='상태 코드에 대한 메세지')
    })


@ns.route('/list')
class GetTagList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('event_id', type=int, help="이벤트 id")
    parser.add_argument('medium_id', type=int, help="매체 id")
    @ns.response(200, '태그 리스트 조회 성공', _Schema.tag_list)
    def get(self):
        """선택한 매체와 이벤트에 연결된 태그들을 조회합니다."""
        args = self.parser.parse_args()
        tags = Tag.get_by_event_and_medium(args['event_id'], args['medium_id'])
        response = [
            {
                "id": tag.id,
                "param": tag.param,
                "script": tag.script
            }
            for tag in tags
        ]
        return response, 200
    

@ns.route('')
class TagCreate(Resource):
    @ns.expect(_Schema.post_fields)
    @ns.response(201, '태그 생성 성공')
    def post(self):
        """선택한 매체와 이벤트에 연결되는 태그를 생성합니다"""
        body = request.json
        event_id = body['event_id']
        medium_id = body['medium_id']
        param = body['param']
        script = body['script']

        Tag.save(event_id, medium_id, param, script)

        return {'msg':'ok'}, 201


@ns.route('/<int:tag_id>')
@ns.doc(params={'tag_id': "태그 id"})
class TagManage(Resource):

    @ns.response(200, '태그 정보 조회 성공', _Schema.basic_fields)
    def get(self, tag_id):
        """tag_id와 일치하는 태그의 상세정보를 가져옵니다"""
        tag = Tag.get_by_id(tag_id)
        response = {
                "id": tag.id,
                "param": tag.param,
                "script": tag.script,
                "event_id": tag.event_id,
                "medium_id": tag.medium_id
            }

        return response, 200
    

    @ns.expect(200, "새로운 태그 데이터", _Schema.put_fields)
    @ns.response(200, "태그 데이터 수정 성공", _Schema.msg_fields)
    def put(self, tag_id):
        """medium_id와 일치하는 매체의 tracking_id 데이터를 수정합니다"""
        body = request.json
        tag = Tag.get_by_id(tag_id)
        tag.update(body['param'], body['script'])
        return {"msg": "ok"}, 200

    
    @ns.response(200, "태그 데이터 삭제 성공", _Schema.msg_fields)
    def delete(self, tag_id):
        """medium_id와 일치하는 매체 엔티티를 삭제합니다"""
        Tag.delete(tag_id)
        return {"msg": "ok"}, 200