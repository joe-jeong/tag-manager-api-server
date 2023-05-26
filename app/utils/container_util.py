def get_container_tag(container_domain):
    return f"fetch('https://localhost:5000/scripts/{container_domain}')" + \
        ".then(response => response.json())" + \
        ".then(data => {" + \
            "const s3Url = data.s3_path;" +\
            "// JavaScript 파일 동적으로 불러오기" + \
            "const script = document.createElement('script');" + \
            "script.src = s3Url;" + \
            "script.onload = function() {" + \
            "// 파일이 성공적으로 로드된 후에 실행할 코드 작성" + \
            "console.log('JavaScript 파일이 성공적으로 로드되었습니다.');" + \
            "};" + \
            "script.onerror = function() {" + \
            "// 파일 로드 중 에러가 발생한 경우 처리할 코드 작성" + \
            "console.error('JavaScript 파일 로드 중 에러가 발생하였습니다.');" + \
            "};" + \
            "// <script> 태그를 <head> 또는 <body>에 추가" + \
            "document.head.appendChild(script);" + \
        "})" + \
        ".catch(error => {" + \
            "console.error('GET 요청 중 오류가 발생하였습니다:', error);" + \
        "});"