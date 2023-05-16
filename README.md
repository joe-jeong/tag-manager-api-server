# Tag Container Manager API Server
## 실행방법
```
pip install -r requirements.txt
flask --app app --debug run --cert=adhoc
```

## Swagger 확인
- https://localhost:5000 입력


## API 명세
### 컨테이너 관련 API
- /containers  POST  새 컨테이너 추가
- /containers  GET 컨테이너 리스트 가져오기
- /containers/{container_domain}  GET  특정 컨테이너 조회
- /containers/{container_domain}  PUT  특정 컨테이너 정보 수정
- /containers/{container_domain}  DELETE  특정 컨테이너 삭제

### 매체 관련 API
- /containers/platforms  GET  서비스에서 사용가능한 플랫폼(GA, Pixel, ...) 리스트 가져오기
- /containers/{container_domain}/mediums  GET  특정 컨테이너의 매체 리스트
- /containers/{container_domain}/mediums  POST  특정 컨테이너에 매체 추가
- /containers/{container_domain}/mediums/{platform_name}  GET  특정 매체 조회
- /containers/{container_domain}/mediums/{platform_name}  PUT  특정 매체 수정
- /containers/{container_domain}/mediums/{platform_name}  DELETE  특정 매체 삭제

### 이벤트 관련 API
- /containers/{container_domain}/events  POST  특정 컨테이너에 이벤트 추가
- /containers/{container_domain}/events  GET  특정 컨테이너의 이벤트 리스트
- /containers/{container_domain}/events/{event_name}  GET  특정 이벤트 조회
- /containers/{container_domain}/events/{event_name}  PUT  특정 이벤트 수정
- /containers/{container_domain}/events/{event_name}  DELETE  특정 이벤트 삭제

### 태그 관련 API (태그의 name은 동일한 컨테이너 내에서는 unique)
- /containers/{container_domain}/tags?platform_name={플랫폼_이름}&event_name={이벤트_이름}  POST  태그 생성
- /containers/{container_domain}/tags?platform_name={플랫폼_이름}&event_name={이벤트_이름}  GET  매체와 이벤트와 연결된 태그 리스트
- /containers/{container_domain}/tags/{tag_name}  GET  특정 태그 조회
- /containers/{container_domain}/tags/{tag_name}  PUT  특정 태그 수정
- /containers/{container_domain}/tags/{tag_name}  DELETE  특정 태그 삭제