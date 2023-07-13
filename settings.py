PORT = 8080
HTTPS_PORT = 8443
ENABLE_HTTPS = False
SSL_KEY = None
SSL_CERT = None

# where to redirect after login/logout - address of client app
KEYCLOAK_REDIRECT_URL = "http://0.0.0.0:8080/"
KEYCLOAK_CLIENT = "fake-client"

BACKEND_URL = "http://0.0.0.0:9999/api/v1"


# for locally rewrite settings add it to settings_local.py
try:
    from settings_local import *
except ModuleNotFoundError as err:
    pass
