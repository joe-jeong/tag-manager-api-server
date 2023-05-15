from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.config.container_config import BUCKET_NAME
from app.utils import container_util, s3_util
from app.model.user import User
from app.model.container import Container
from flask_restx import Namespace, Resource, fields, reqparse

ns = Namespace(
    name='container',
    description='컨테이너 관련 API'
    )

class _Schema():
    post_fields = ns.model('컨테이너 생성시 필요 데이터', {
        'name': fields.String(description='Container Name', example='test-container-1') ,
        'description': fields.String(description='Container Description', example='Container for tag management'),
        'domain': fields.String(description='Domain of the Container', example='https://www.samsung.com')
    })

    basic_fields = ns.model('컨테이너 기본 정보', {
        'id': fields.Integer(description='Container ID', example=1),
        'name': fields.String(description='Container Name', example='test-container-1'),
        'domain': fields.String(description='Domain of the Container', example='https://www.samsung.com/')
    })

    detail_fields = ns.inherit('컨테이너 상세 정보', basic_fields, {
        'description': fields.String(description='Container Description', example='Container for tag management')
    })

    msg_fields = ns.model('상태 코드에 따른 설명', {
        'msg': fields.String(description='상태 코드에 대한 메세지', example='ok')
    })

    container_list = fields.List(fields.Nested(basic_fields))


@ns.route('/list')
@ns.doc(params={'user_id': {'description': '유저 id', 'in': 'query', 'type': 'int'}})
class ContainerList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, help="유저 id")
    @ns.response(200, '컨테이너 리스트 조회 성공', _Schema.container_list)
    def get(self):
        """현재 회원의 컨테이너 리스트를 가져옵니다."""
        args = self.parser.parse_args()
        containers = User.get_containers(args['user_id'])
        response = [
            {
                "id": container.id,
                "name": container.name,
                "domain": container.domain
            }
            for container in containers
        ]
        
        return response, 200


@ns.route('')
@ns.doc(params={'user_id': {'description': '유저 id', 'in': 'query', 'type': 'int'}})
class ContainerCreate(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, help="유저 id")

    @ns.expect(_Schema.post_fields)
    @ns.response(201, '컨테이너 생성 성공', _Schema.msg_fields)
    def post(self):
        """새 컨테이너를 추가합니다."""
        args = self.parser.parse_args()
        body = request.json
        name = body['name']
        domain = body['domain']
        desc = body['description']

        Container.save(name=name, domain=domain, description=desc, user_id=args['user_id']) 

        return {'msg':'ok'}, 201
    

@ns.route('/<string:container_name>')
@ns.doc(params={'container_name': '컨테이너의 이름'})
class ContainerManage(Resource):
    
    @ns.response(200, "컨테이너 정보 조회 성공", _Schema.detail_fields)
    def get(self, container_name):
        """container_name와 일치하는 컨테이너의 상세 정보를 가져옵니다."""
        container = Container.get_by_name(container_name)
        response = {
            "id" : container.id,
            "name" : container.name,
            "domain" : container.domain,
            "description" : container.description
        }

        return response, 200

    
    @ns.expect(200, "새로운 컨테이너 데이터", _Schema.post_fields)
    @ns.response(200, '컨테이너 정보 수정 성공', _Schema.msg_fields)
    def put(self, container_name):
        """container_name와 일치하는 컨테이너의 정보를 수정합니다."""
        data = request.json
        name = data['name']
        domain = data['domain']
        desc = data['description']

        container = Container.get(container_name)
        container.update(name, domain, desc)

        return jsonify({"status": "ok"}), 200


    
    @ns.response(201, '컨테이너 삭제 성공', _Schema.msg_fields)
    def delete(self, container_name):
        """container_name와 일치하는 컨테이너를 삭제합니다."""
        user_id = get_jwt_identity()
        Container.delete(user_id, container_name)

        return jsonify({"status": "ok"}), 200
