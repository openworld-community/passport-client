from urllib.parse import urlparse
from urllib.parse import parse_qs

from aiohttp import web, ClientSession
import aiohttp_jinja2

from settings import KEYCLOAK_URL, KEYCLOAK_REDIRECT_URL, KEYCLOAK_CLIENT, BACKEND_URL


async def login(request):
    '''redirects to keycloak login url'''
    url = KEYCLOAK_URL + "auth"
    response_mode = 'query'  # 'fragment' sets code to URL fragment, 'form_post' does POST, 'query' does GET
    url += f'?client_id={KEYCLOAK_CLIENT}&redirect_uri={KEYCLOAK_REDIRECT_URL}&response_mode={response_mode}&response_type=code&scope=openid'
    return web.HTTPFound(url)


async def logout(request):
    '''redirects to keycloak logout url and removes jwt from cookies'''
    url = KEYCLOAK_URL + "logout"
    url += f'?client_id={KEYCLOAK_CLIENT}&post_logout_redirect_uri={KEYCLOAK_REDIRECT_URL}'
    response = web.HTTPFound(url)
    response.del_cookie('access')
    response.del_cookie('refresh')
    return response

# refresh:
# https://stackoverflow.com/questions/51386337/refresh-access-token-via-refresh-token-in-keycloak

# TODO: move from client to backend?
async def keycloak_request_token(code):
    '''retrieves JWT from keycloak server by code'''
    url = KEYCLOAK_URL + "token"
    body = f"code={code}&grant_type=authorization_code&client_id={KEYCLOAK_CLIENT}&redirect_uri={KEYCLOAK_REDIRECT_URL}"
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    async with ClientSession(headers=headers) as session:
        async with session.post(url, data=bytes(body.encode())) as resp:
            return await resp.json()


async def request_token(request):
    '''sets access/refresh tokens to cookies and redirects to /'''
    # html POST form can't send json, so parsing params as query string
    params = await request.text()
    data = parse_qs(urlparse('?' + params).query)
    code = data['code'][0]

    response = web.HTTPFound('/')

    token = await keycloak_request_token(code)
    if not token or 'error' in token:
        response.del_cookie('access')
        print(code, token)
    else:
        # available keys in token:
        # dict_keys(['access_token', 'expires_in', 'refresh_expires_in', 'refresh_token',
        # 'token_type', 'id_token', 'not-before-policy', 'session_state', 'scope'])
        response.cookies['access'] = token.get('access_token')
        response.cookies['refresh'] = token.get('refresh_token')

    return response


async def get_user(request):
    '''
    TODO: implement backend.
    should take access token from request cookies and return user info from its DB like this:
    >>> token = request.cookies.get('access')
    >>> data = parse_jwt(token)
    >>> user_info = get_user_from_db(data['name'])
    '''
    url = BACKEND_URL + 'get_user'
    async with ClientSession(cookies=request.cookies) as session:
        async with session.get(url) as resp:
            # TODO: change to json once endpoint is ready
            data = await resp.text()
    return web.Response(text=data)


async def index(request):
    # if code is set in GET params, it was made by keycloak redirect after auth
    code = request.rel_url.query.get('code')
    response = aiohttp_jinja2.render_template(
        "login.html", request, context={'keycloak_code': code})

    return response
