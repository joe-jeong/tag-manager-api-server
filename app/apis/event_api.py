from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

from app.model.event import Event
from app.model.container import Container
from flask_restx import Namespace, Resource, fields, reqparse

ns = Namespace(
    name='event',
    description='이벤트 관련 API',
    path='/'
)

class _Schema():

    post_fields = ns.model('이벤트 생성/수정 시 필요 데이터', {
        'name': fields.String(desciprtion='Event name', example='test-event-1'),
        'func_code': fields.String(description='Event function js code', example='button1.addEventListener("click", (ev)=> ...)'),
        'url_reg': fields.String(description='Regular expression for the url of the page where the event will be triggered', example='/^https?:\/\/(?:www\.)?[-a-zA-Z ...')
    })

    basic_fields = ns.model('이벤트 기본정보', {
        'name': fields.String(description='event name', example='test-event-1')
    })

    detail_fields = ns.inherit('이벤트 상세정보', basic_fields, {
        'func_code': fields.String(description='event function js code', example='button1.addEventListener("click", (ev)=> ...)'),
        'url_reg': fields.Integer(desciption='Regular expression for the url of the page where the event will be triggered', example='/^https?:\/\/(?:www\.)?[-a-zA-Z ...')
    })

    event_list = fields.List(fields.Nested(basic_fields))

    msg_fields = ns.model('상태 코드에 따른 설명', {
        'msg': fields.String(description='상태 코드에 대한 메세지', example='처리 내용')
    })


@ns.route('/containers/<string:container_domain>/events')
@ns.doc(params={'container_domain': '컨테이너 도메인'})
class EventCreate(Resource):

    @ns.response(200, '이벤트 리스트 조회 성공', _Schema.event_list)
    def get(self, container_domain):
        """현재 컨테이너의 이벤트 리스트를 가져옵니다"""
        events = Container.get_events(container_domain)
        response = [
            {
                "name": event.name
            }
            for event in events
        ]
        return response, 200
    

    @ns.expect(_Schema.post_fields)
    @ns.response(201, '컨테이너에 이벤트 추가 성공', _Schema.msg_fields)
    @ns.response(400, '컨테이너에 이벤트 추가 실패', _Schema.msg_fields)
    def post(self, container_domain):
        """현재 컨테이너에 이벤트를 추가합니다"""
        body = request.json
        name = body['name']
        func_code = body['func_code']
        url_reg = body['url_reg']

        event = Event.save(container_domain, name, func_code, url_reg)

        if event:
            return {'msg':'ok'}, 201
        return {'msg':'컨테이너 내에 동일한 이름의 이벤트가 이미 존재합니다.'}, 400


@ns.route('/containers/<string:container_domain>/events/<string:event_name>')
@ns.doc(params={'container_domain': '컨테이너 도메인', 'event_name': '이벤트 이름'})
class EventManage(Resource):

    @ns.response(200, "이벤트 정보 조회 성공", _Schema.detail_fields)
    def get(self, container_domain, event_name):
        """특정 컨테이너 내에서 event_name와 일치하는 이벤트의 상세정보를 가져옵니다"""
        event = Event.get_by_container_and_name(container_domain, event_name)
        response = {
            "name": event.name,
            "func_code": event.func_code,
            "url_reg": event.url_reg
        }
        return response, 200
    

    @ns.expect(200, "새로운 매체 데이터", _Schema.post_fields)
    @ns.response(200, "매체 tracking_list 수정 성공", _Schema.msg_fields)
    def put(self, container_domain, event_name):
        """특정 컨테이너 내에서 event_domain와 일치하는 event의 데이터를 수정합니다"""
        body = request.json
        event = Event.get_by_container_and_name(container_domain, event_name)
        event.update(body['name'], body['func_code'], body['url_reg'])

        return {"msg": "ok"}, 200

    
    @ns.response(200, "이벤트 데이터 삭제 성공", _Schema.msg_fields)
    def delete(self, container_domain, event_name):
        """특정 컨테이너 내에서 event_name와 일치하는 event 엔티티를 삭제합니다"""
        Event.delete_by_name(container_domain, event_name)
        return {"msg": "ok"}, 200
