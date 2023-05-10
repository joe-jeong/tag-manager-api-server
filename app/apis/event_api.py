from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

from app.model.event import Event
from app.model.container import Container
from flask_restx import Namespace, Resource, fields, reqparse

ns = Namespace(
    name='event',
    description='이벤트 관련 API'
)

class _Schema():

    post_fields = ns.model('이벤트 생성/수정 시 필요 데이터', {
        'name': fields.String(desciprtion='Event name'),
        'func_code': fields.String(description='Event function js code'),
        'url_reg': fields.String(description='Regular expression for the url of the page where the event will be triggered'),
        "container_id": fields.Integer(description='Container ID')
    })

    basic_fields = ns.model('이벤트 기본정보', {
        'id': fields.Integer(description='event id'),
        'name': fields.String(description='event name')
    })

    detail_fields = ns.inherit('이벤트 상세정보', basic_fields, {
        'func_code': fields.String(description='event function js code'),
        'url_reg': fields.Integer(desciption='Regular expression for the url of the page where the event will be triggered')
    })

    event_list = fields.List(fields.Nested(basic_fields))

    msg_fields = ns.model('상태 코드에 따른 설명', {
        'msg': fields.String(description='상태 코드에 대한 메세지')
    })

@ns.route('/list')
@ns.doc(params={'container_id': {'description': '컨테이너 id', 'in': 'query', 'type': 'int'}})
class EventList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('container_id', type=int, help="컨테이너의 id")
    @ns.response(200, '이벤트 리스트 조회 성공', _Schema.event_list)
    def get(self):
        """현재 컨테이너의 이벤트 리스트를 가져옵니다"""
        args = self.parser.parse_args()
        events = Container.get_events(args['container_id'])
        response = [
            {
                "id": event.id,
                "name": event.name
            }
            for event in events
        ]

        return response, 200


@ns.route('')
class EventCreate(Resource):
    @ns.expect(_Schema.post_fields)
    @ns.response(201, '컨테이너에 이벤트 추가 성공', _Schema.msg_fields)
    def post(self):
        """현재 컨테이너에 이벤트를 추가합니다"""
        body = request.json
        container_id = body['container_id']
        name = body['name']
        func_code = body['func_code']
        url_reg = body['url_reg']

        Event.save(container_id, name, func_code, url_reg)

        return {'msg':'ok'}, 201


@ns.route('/<int:event_id>')
@ns.doc(params={'event_id': '이벤트 id'})
class EventManage(Resource):

    @ns.response(200, "이벤트 정보 조회 성공", _Schema.detail_fields)
    def get(self, event_id):
        """event_id와 일치하는 매체의 상세정보를 가져옵니다"""
        event = Event.get(event_id)
        response = {
            "id": event.id,
            "name": event.name,
            "func_code": event.func_code,
            "url_reg": event.url_reg
        }
        return response, 200
    
    @ns.expect(200, "새로운 매체 데이터", _Schema.post_fields)
    @ns.response(200, "매체 tracking_list 수정 성공", _Schema.msg_fields)
    def put(self, event_id):
        """event_id와 일치하는 event의 데이터를 수정합니다"""
        body = request.json
        event = Event.get(event_id)
        event.update(body['name'], body['func_code'], body['url_reg'])

        return {"msg": "ok"}, 200

    
    @ns.response(200, "이벤트 데이터 삭제 성공", _Schema.msg_fields)
    def delete(self, event_id):
        """event_id와 일치하는 event 엔티티를 삭제합니다"""
        Event.delete(event_id)
        return {"msg": "ok"}, 200