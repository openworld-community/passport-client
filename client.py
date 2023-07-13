import json
from urllib.parse import urlparse
from urllib.parse import parse_qs

from aiohttp import web, ClientSession
import aiohttp_jinja2

from settings import KEYCLOAK_REDIRECT_URL, KEYCLOAK_CLIENT, BACKEND_URL


async def request_backend(endpoint, data=None, method='POST', headers=None, wrap_to_response=True):
    '''
    wrapper to make queries to backend.
    may return:
        - web.HTTPFound if got redirect
        - web.json_response if wrap_to_response is true
        - dict otherwise
    '''
    url = BACKEND_URL + endpoint
    async with ClientSession(headers=headers) as session:
        meth = session.post if method == 'POST' else session.get
        if data:
            data = json.dumps(data)
        async with meth(url, data=data, allow_redirects=False) as resp:
            if loc := resp.headers.get('location'):
                return web.HTTPFound(loc)
            data = await resp.json()
            if wrap_to_response:
                return web.json_response(data, status=resp.status)
            return data


async def login(request):
    '''redirects to keycloak login url'''
    data = {'redirect_uri': KEYCLOAK_REDIRECT_URL, 'client_id': KEYCLOAK_CLIENT}
    response = await request_backend('/login', data)
    return response


async def logout(request):
    '''redirects to keycloak logout url and removes jwt from cookies'''
    data = {'redirect_uri': KEYCLOAK_REDIRECT_URL, 'client_id': KEYCLOAK_CLIENT}
    response = await request_backend('/logout', data)
    response.del_cookie('access')
    response.del_cookie('refresh')
    return response


async def request_token(request):
    '''sets access/refresh tokens to cookies and redirects to /'''
    # html POST form can't send json, so parsing params as query string
    params = await request.text()
    data = parse_qs(urlparse('?' + params).query)
    code = data['code'][0]

    data = {'redirect_uri': KEYCLOAK_REDIRECT_URL, 'client_id': KEYCLOAK_CLIENT, 'code': code}
    token = await request_backend('/token', data, wrap_to_response=False)

    response = web.HTTPFound('/')
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
    access = request.cookies.get('access')
    headers = {'Authorization': 'Bearer ' + access}
    return await request_backend('/user/all_data', method='GET', headers=headers)


async def index(request):
    # if code is set in GET params, it was made by keycloak redirect after auth
    code = request.rel_url.query.get('code')
    response = aiohttp_jinja2.render_template(
        "login.html", request, context={'keycloak_code': code, 'backend_url': BACKEND_URL})

    return response
