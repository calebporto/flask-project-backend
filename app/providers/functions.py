from app.models.basemodels import Permission, Tithe_List, User_With_Data
from flask import flash, request
from json import loads
import requests
import os
from datetime import date

API_URL = os.environ["API_URL"]
API_KEY = os.environ["API_KEY"]
AUTHORIZED_ID = os.environ["AUTHORIZED_ID"]
headers = {'api_key': API_KEY, 'id': AUTHORIZED_ID}

# Faz requisiões post
def post_request(endpoint, data):
    return requests.post(f'{API_URL}{endpoint}', data, headers=headers)

# Faz requisições get
def get_request(endpoint):
    return requests.get(f'{API_URL}{endpoint}', headers=headers)

# Faz requisições delete
def delete_request(endpoint):
    return requests.delete(f'{API_URL}{endpoint}', headers=headers)

# Altera permissões de acesso do painel de membros
def update_permissions(data):
    form = request.form.get(data)
    if form:
        if int(form) == 1:
            match data:
                case 'permission1':
                    send = Permission(
                        name='painel',
                        permission1=False
                    )
                case 'permission2':
                    send = Permission(
                        name='painel',
                        permission2=False
                    )
                case 'permission3':
                    send = Permission(
                        name='painel',
                        permission3=False
                    )
                case 'permission4':
                    send = Permission(
                        name='painel',
                        permission4=False
                    )
                case 'permission5':
                    send = Permission(
                        name='painel',
                        permission5=False
                    )
                case 'permission6':
                    send = Permission(
                        name='painel',
                        permission6=False
                    )

            response = post_request('/permissions-update', send.json())
            if response.status_code == 200:
                if loads(response.text)['confirm'] == True:
                    return True
                else:
                    return False
            else:
                return False
        elif int(form) == 2:
            match data:
                case 'permission1':
                    send = Permission(
                        name='painel',
                        permission1=True
                    )
                case 'permission2':
                    send = Permission(
                        name='painel',
                        permission2=True
                    )
                case 'permission3':
                    send = Permission(
                        name='painel',
                        permission3=True
                    )
                case 'permission4':
                    send = Permission(
                        name='painel',
                        permission4=True
                    )
                case 'permission5':
                    send = Permission(
                        name='painel',
                        permission5=True
                    )
                case 'permission6':
                    send = Permission(
                        name='painel',
                        permission6=True
                    )
            response = post_request('/permissions-update', send.json())
            if response.status_code == 200:
                if loads(response.text)['confirm'] == True:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False

# Retorna o saldo do mês e o saldo total
def get_balance():
    class Balance:
        def __init__(self, period_balance, total_balance):
            self.period_balance = period_balance
            self.total_balance = total_balance
    
    start = date(date.today().year, date.today().month, 1)
    end = date.today()
    balance_response = get_request(f'/finance-values/{start}/{end}')
    
    offer_sum = round(sum(loads(balance_response.text)['offers']), 2)
    tithe_sum = round(sum(loads(balance_response.text)['tithes']), 2)
    expense_sum = round(sum(loads(balance_response.text)['expenses']), 2)
    previous_balance = round(sum(loads(balance_response.text)['previous_balance']), 2)
    
    balance1 = offer_sum + tithe_sum - expense_sum  # period_balance
    balance2 = balance1 + previous_balance  # total_balance
    period_balance = (((f'R$ {(balance1):,.2f}').replace(',','v')).replace('.',',')).replace('v','.')
    total_balance = (((f'R$ {(balance2):,.2f}').replace(',','v')).replace('.',',')).replace('v','.')
    return Balance(period_balance, total_balance)

def get_title_list(tithe_list):
    if tithe_list.text == 'null':
        tithe_list_data = [Tithe_List]
        flash('Erro no carregamento dos dados')
    else:
        tithe_list_dict = loads(tithe_list.text)
        tithe_list_data = tithe_list_dict['tithe_list']
        for i, linha in enumerate(tithe_list_data):
            linha = Tithe_List(value=linha['value'], tithe_date=linha['tithe_date'], treasurer=linha['treasurer'])
            linha.value = f'R$ {linha.value:,.2f}'
            linha.tithe_date = (linha.tithe_date).strftime('%d/%m/%Y')
            linha.treasurer = (linha.treasurer).title()
            tithe_list_data[i] = linha
    return tithe_list_data

def get_user_func(get_user):
    if get_user.text == 'null':
        user_data = User_With_Data
        flash('Erro no carregamento dos dados')
    else:
        user_data = User_With_Data(**loads(get_user.text))
        if user_data.gender == 'm':
            user_data.gender = 'Masculino'
        else:
            user_data.gender = 'Feminino'
        user_data.birth = (user_data.birth).strftime('%d/%m/%Y')
        user_data.name = (user_data.name).title()
        user_data.address = (user_data.address).title()
        return user_data