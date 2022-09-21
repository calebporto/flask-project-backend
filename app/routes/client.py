from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, request, flash, redirect, session
from app.providers.hash_provider import *
from app.providers.requests import *
from app.models.basemodels import *
from app.config import API_URL
from datetime import datetime
from app.models.user import *
from typing import List
from json import loads
from app import app
import requests

@app.route('/home')
@app.route('/')
def home():
    return render_template('client/home.html')

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        address = f'{request.form.get("logradouro")} {request.form.get("numero")}, {request.form.get("bairro")}, {request.form.get("cidade")} - {request.form.get("uf")}'
        senha = get_password_hash(request.form.get('senha'))
        send = Send_User(
            name= request.form.get('nome').lower(), 
            email= request.form.get('email').lower(), 
            hash= senha, 
            cep= request.form.get('cep').lower(), 
            address= address.lower(), 
            gender = request.form.get('sexo').lower(),
            tel= request.form.get('tel').lower(), 
            birth= datetime.strptime(request.form.get('nascimento'), '%d/%m/%Y').date())

        response = post_request('/send-user', send.json())
        
        if response.status_code == 200:
            dados = loads(response.text)['confirm']

            if dados == False:
                flash('E-mail já cadastrado.')
                return redirect('/cadastrar')
            else:
                flash('Cadastro enviado para análise.')
                return redirect('/cadastrar')
        else:
            flash('Algo deu errado. Tente novamente mais tarde.')
            return redirect('/cadastrar')
    else:
        return render_template('client/cadastrar.html')

@app.route('/entrar', methods=['GET', 'POST'])
def entrar():
    if request.method == 'POST':
        send = Get_User(
            email= request.form.get('login').lower()
        )
        response = post_request('/get-user', send.json())
        if response.status_code == 200:
            # Criar sessão de usuário
            if response.text == 'null':
                flash('Usuário não cadastrado')
                return redirect('/entrar')
            
            response_data = User_Loader(**loads(response.text))
            user = User(
                response_data.id, response_data.name, 
                response_data.email, response_data.hash, 
                response_data.is_admin, response_data.is_designer)
            
            if not verify_password(request.form.get('senha'), user.hash):
                flash('Senha Incorreta!')
                return redirect('/entrar')
            
            login_user(user, remember=True)

            if 'next' in session:
                next = session['next']

                if next is not None:
                    return redirect(next)
            
            return redirect('/painel')
        else:
            flash('Algo deu errado. Tente novamente mais tarde.')
            return redirect('/entrar')
    else:
        try:
            if current_user.name:
                return redirect('/painel')
        except AttributeError:
            return render_template('client/entrar.html')
        except:
            return 'Erro Inesperado'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/home')

@app.route('/painel')
@login_required
def painel():
    def get_title_list(tithe_list):
        if tithe_list.text == 'null':
            tithe_list_data = [Tithe_List]
            flash('Algo deu errado.')
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
            flash('Algo deu errado.')
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

    get_user = get_request(f'/get-user-with-data/{current_user.id}')
    time = 365
    tithe_list = get_request(f'/tithe-list/{time}/{current_user.id}/2')

    if get_user.status_code == 200 and tithe_list.status_code == 200:
        user_data = get_user_func(get_user)
        tithe_list_data = get_title_list(tithe_list)
        return render_template('client/painel.html', user_data=user_data, tithe_list_data=tithe_list_data)
    
    elif get_user.status_code == 200 and tithe_list.status_code != 200:
        user_data = get_user_func(get_user)
        tithe_list_data = [Tithe_List]
        flash('Algo deu errado.')
        return render_template('client/painel.html', user_data=user_data, tithe_list_data=tithe_list_data)

    elif get_user.status_code != 200 and tithe_list.status_code == 200:
        user_data = User_With_Data
        tithe_list_data = get_title_list(tithe_list)
        flash('Algo deu errado.')
        return render_template('client/painel.html', user_data=user_data, tithe_list_data=tithe_list_data)

    else:
        user_data = User_With_Data
        tithe_list_data = Tithe_List
        flash('Algo deu errado')
        return render_template('client/painel.html', user_data=user_data, tithe_list_data=tithe_list_data)

@app.route('/painel/alterar-dados', methods=['POST'])
def post_user_update():
    user = User_Update(id=request.form['id'])
    user.name = request.form['nome'].lower() if request.form['nome'] else None
    user.email = request.form['email'].lower() if request.form['email'] else None
    user.cep = request.form['cep'].lower() if request.form['cep'] else None
    user.address = request.form['endereco'].lower() if request.form['endereco'] else None
    user.gender = request.form['sexo'].lower() if request.form['sexo'] else None
    user.tel = request.form['celular'].lower() if request.form['celular'] else None

    if request.form['nascimento']:
        birth = datetime.strptime(request.form['nascimento'], '%d/%m/%Y').date()
        user.birth = birth

    response = post_request('/user-update', user.json())
    if response.status_code == 200:
            dados = loads(response.text)['confirm']

            if dados == False:
                flash('Não foi possível atualizar os seus dados.')
                return redirect('/painel')
            else:
                flash('Dados atualizados.')
                return redirect('/painel')
    else:
        flash('Algo deu errado. Tente novamente mais tarde.')
        return redirect('/painel')

@app.route('/painel/alterar-dados/<user_id>', methods=['GET'])
def get_user_update(user_id: int):
        
    get_user = get_request(f'/get-user-with-data/{user_id}')
    if get_user.text == 'null':
        user_data = User_With_Data
        flash('Algo deu errado.')
        return render_template('client/alterar-dados.html', user_data=user_data)
    else:
        user_data = User_With_Data(**loads(get_user.text))
        if user_data.gender == 'm':
            user_data.gender = 'Masculino'
        else:
            user_data.gender = 'Feminino'
        user_data.birth = (user_data.birth).strftime('%d/%m/%Y')
        return render_template('client/alterar-dados.html', user_data=user_data)