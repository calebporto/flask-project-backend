from json import loads
from flask import redirect
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
from flask_login import UserMixin
from app.models.basemodels import Get_User, User_Loader
from app import login_manager
from app.providers.functions import post_request


Base = declarative_base()

@login_manager.user_loader
def load_user(user_id):
    send = Get_User(alternative_id=user_id)
    response = post_request('/get-user', send.json()).text
    if response == 'null':
        return redirect('/logout')
    user = User_Loader(**loads(response))
    return User(user.id, user.alternative_id, user.name, user.email, user.hash, user.is_admin, user.is_treasurer, user.is_secretary, user.is_adviser, user.is_designer)

class User(Base, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    alternative_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_treasurer = Column(Boolean, default=False)
    is_secretary = Column(Boolean, default=False)
    is_adviser = Column(Boolean, default=False)
    is_designer = Column(Boolean, default=False)

    def __init__(self, id, alternative_id, name, email, hash, is_admin=False, is_treasurer=False, is_secretary=False, is_adviser=False, is_designer=False):
        self.id = id
        self.alternative_id = alternative_id
        self.name = name
        self.email = email
        self.hash = hash
        self.is_admin = is_admin
        self.is_treasurer = is_treasurer
        self.is_secretary = is_secretary
        self.is_adviser = is_adviser
        self.is_designer = is_designer

    def get_id(self):
        print('ok')
        return str(self.alternative_id)

    def __repr__(self):
        return f'Pessoa({self.name})'