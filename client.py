from urllib.parse import urlparse
from urllib.parse import parse_qs

from aiohttp import web, ClientSession
import aiohttp_jinja2

from settings import KEYCLOAK_URL, KEYCLOAK_REDIRECT_URL, KEYCLOAK_CLIENT


async def login(request):
    url = KEYCLOAK_URL + "auth"
    response_mode = 'fragment'  # sets code to URL fragment. form_post does POST
    url += f'?client_id={KEYCLOAK_CLIENT}&redirect_uri={KEYCLOAK_REDIRECT_URL}&response_mode={response_mode}&response_type=code&scope=openid'
    return web.HTTPFound(url)


async def logout(request):
    url = KEYCLOAK_URL + "logout"
    url += f'?client_id={KEYCLOAK_CLIENT}&post_logout_redirect_uri={KEYCLOAK_REDIRECT_URL}'
    response = web.HTTPFound(url)
    response.del_cookie('access')
    response.del_cookie('refresh')
    return response

# refresh:
# https://stackoverflow.com/questions/51386337/refresh-access-token-via-refresh-token-in-keycloak

async def request_token(request):
    params = await request.text()
    data = parse_qs(urlparse('?' + params).query)
    code = data['code'][0]
    print(f"request token for {code}")

    url = KEYCLOAK_URL + "token"
    body = f"code={code}&grant_type=authorization_code&client_id={KEYCLOAK_CLIENT}&redirect_uri={KEYCLOAK_REDIRECT_URL}"
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    async with ClientSession(headers=headers) as session:
        async with session.post(url, data=bytes(body.encode())) as resp:
            data = await resp.json()
    response = web.HTTPFound('/')
    # available keys:
    # dict_keys(['access_token', 'expires_in', 'refresh_expires_in', 'refresh_token', 'token_type', 'id_token', 'not-before-policy', 'session_state', 'scope'])
    if 'error' in data:
        print(data)
        response.del_cookie('access')
    else:
        response.cookies['access'] = data.get('access_token')
        response.cookies['refresh'] = data.get('refresh_token')
    return response


async def index(request):
    response = aiohttp_jinja2.render_template(
        "login.html", request, context={})
    return response
