from web_server import app
from asgiref.wsgi import WsgiToAsgi

asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    asgi_app.run()
