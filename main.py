import os

from aiohttp import web
import jinja2
import aiohttp_jinja2

from client import index, login, logout, request_token
from settings import PORT

app = web.Application()
aiohttp_jinja2.setup(
    app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
)

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
    web.run_app(app, port=PORT)
