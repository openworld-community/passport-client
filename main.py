import os
import ssl

from aiohttp import web
import jinja2
import aiohttp_jinja2

from client import index, login, logout, request_token
from settings import PORT, ENABLE_HTTPS, HTTPS_PORT, SSL_KEY, SSL_CERT

app = web.Application()
aiohttp_jinja2.setup(
    app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
)

port = PORT
ssl_context = None
if ENABLE_HTTPS:
    port = HTTPS_PORT
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(SSL_CERT, keyfile=SSL_KEY)

app.add_routes([
    web.get("/", index),
    web.get("/login", login),
    web.get("/logout", logout),
    web.post("/request_token", request_token),
    web.static('/static', 'static'),
])


async def on_startup(app):
    pass


app.on_startup.append(on_startup)

if __name__ == '__main__':
    web.run_app(app, port=port, ssl_context=ssl_context)
