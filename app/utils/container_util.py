def get_container_tag(container_id):
    return f"fetch(`http://localhost:5000/container/{container_id}/scripts`)"+\
        ".then(response => response.json())"+\
        ".then(urls => {urls.forEach(url => {"+\
            "const script = document.createElement('script');"+\
            "script.src = url;"+\
            "document.body.appendChild(script);"+\
        "});"+\
    "});"