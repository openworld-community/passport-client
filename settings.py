PORT = 8080

KEYCLOAK_REALM = "peredelano"
KEYCLOAK_REDIRECT_URL = "http://0.0.0.0:8080/"
KEYCLOAK_CLIENT = "fake-client"

# for locally rewrite settings add it to settings_local.py
try:
    from settings_local import *
except ModuleNotFoundError as err:
    pass


KEYCLOAK_URL = f"https://keycloak.regela.ru/realms/{KEYCLOAK_REALM}/protocol/openid-connect/"
