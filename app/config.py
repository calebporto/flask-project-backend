from dotenv import load_dotenv
load_dotenv()

import os

USE_SESSION_FOR_NEXT = True # Excluindo a variável 'next' da string de recirecionamento do login_required
REMEMBER_COOKIE_REFRESH_EACH_REQUEST = False
SECRET_KEY = os.environ['SECRET_KEY']
API_URL = os.environ['API_URL']
SECRET_KEY = SECRET_KEY
API_URL = API_URL