PORT = 8080
SSL_KEY = None
SSL_CERT = None

KEYCLOAK_REALM = "peredelano"
KEYCLOAK_REDIRECT_URL = "http://0.0.0.0:8080/"
KEYCLOAK_CLIENT = "fake-client"
KEYCLOAK_URL = f"https://keycloak.regela.ru/realms/{KEYCLOAK_REALM}/protocol/openid-connect/"

BACKEND_URL = "http://0.0.0.0:8888"


# for locally rewrite settings add it to settings_local.py
try:
    from settings_local import *
except ModuleNotFoundError as err:
    pass
