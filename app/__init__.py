from flask import Flask
from app.config import *
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['USE_SESSION_FOR_NEXT'] = USE_SESSION_FOR_NEXT  # Excluindo a variável 'next' da string de recirecionamento do login_required
app.config['REMEMBER_COOKIE_DURATION'] = REMEMBER_COOKIE_DURATION
app.config['REMEMBER_COOKIE_REFRESH_EACH_REQUEST'] = REMEMBER_COOKIE_REFRESH_EACH_REQUEST

login_manager = LoginManager(app)
login_manager.login_view = "/entrar"  # Definindo a página de redirecionamento caso o usuário não esteja logado através de login_required
login_manager.login_message = u'Por favor, faça login para acessar esta página'

from app.routes import client, admin