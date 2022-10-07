from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, request, flash, redirect, session
from app.providers.decorators import designer_kick
from app.providers.hash_provider import *
from app.providers.functions import *
from app.models.basemodels import *
from datetime import timedelta
from app.config import API_URL
from datetime import datetime
from app.models.user import *
from typing import List
from json import loads
from app import app

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
                response_data.is_admin, response_data.is_treasurer, 
                response_data.is_secretary, response_data.is_adviser, response_data.is_designer)
            
            if not verify_password(request.form.get('senha'), user.hash):
                flash('Senha Incorreta!')
                return redirect('/entrar')
            
            login_user(user, remember=True)

            if 'next' in session:
                next = session['next']

                if next is not None:
                    return redirect(next)
            
            if user.is_designer == True:
                return redirect('/home')
            else:
                return redirect('/painel')
        else:
            flash('Algo deu errado. Tente novamente mais tarde.')
            return redirect('/entrar')
    else:
        try:
            # Impedindo designer de acessar painel
            if current_user.name and current_user.is_designer == True:
                flash('Você já está logado no sistema.')
                return redirect('/home')
            # Caso não seja designer e esteja logado, redireciona para o painel
            elif current_user.name and current_user.is_designer == False:
                return redirect('/painel')
            else:
            # Se não estiver logado, acessa a página entrar
                return redirect ('/entrar')
            
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
@designer_kick
@login_required
def painel():
    
    permissions, user_data, tithe_list_data, balance = None, None, None, None

    permission_response = get_request('/get-permissions/painel')
    if permission_response.status_code == 200:
        if permission_response.text != 'null':
            permissions = Permission(**loads(permission_response.text))
            if permissions.permission1 == True:
                balance = get_balance()
            if permissions.permission4 == True:
                get_user = get_request(f'/get-user-with-data/{current_user.id}')
                user_data = get_user_func(get_user)
            if permissions.permission6 == True:
                tithe_list = get_request(f'/tithe-list/365/{current_user.id}/2')
                tithe_list_data = get_title_list(tithe_list)
        else:
            flash('Erro no carregamento dos dados')
    else:
        flash('Erro no carregamento dos dados')
    
    return render_template('client/painel.html', permissions=permissions, user_data=user_data, tithe_list_data=tithe_list_data, balance=balance)

@app.route('/painel/alterar-dados', methods=['POST'])
@designer_kick
@login_required
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
@designer_kick
@login_required
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
        print(user_data.birth)
        user_data.birth = (user_data.birth).strftime('%d/%m/%Y')
        return render_template('client/alterar-dados.html', user_data=user_data)

@app.route('/painel/relatorios-financeiros')
@login_required
def relatorios_financeiros_client():
    try:
        start = date(date.today().year, date.today().month, 1) - timedelta(days=366)
        end = date.today()
        response = get_request(f'/finance-list/{start}/{end}')
        if response.status_code == 200:
            if response.text != 'null':
                finance_list = loads(response.text)
                for i, item in enumerate(finance_list):
                    start = (datetime.strptime(item['start'], '%Y-%m-%d'))
                    ref = f'{str(start.month).rjust(2, "0")}/{start.year}'
                    entry = (((f'R$ {item["entry"]:,.2f}').replace(',','v')).replace('.',',')).replace('v','.')
                    issues = (((f'R$ {item["issues"]:,.2f}').replace(',','v')).replace('.',',')).replace('v','.')
                    period_balance = (((f'R$ {item["period_balance"]:,.2f}').replace(',','v')).replace('.',',')).replace('v','.')
                    total_balance = (((f'R$ {item["total_balance"]:,.2f}').replace(',','v')).replace('.',',')).replace('v','.')
                    data = History_Finance(
                        ref=ref,
                        entry=entry,
                        issues=issues,
                        period_balance=period_balance,
                        total_balance=total_balance
                    )
                    finance_list[i] = data
            else:
                flash('Algo deu errado.')
                return redirect('/painel')    
            return render_template('client/relatorios-financeiros.html', finance_list=finance_list)
        else:
            flash('Algo deu errado.')
            return redirect('/painel')
    except Exception as error:
        print(str(error))
        flash('Algo deu errado.')
        return redirect('/painel')

@app.route('/painel/rol-de-membros')
@login_required
def rol_de_membros_client():
    try:
        response = get_request('/user-list')
        if response.status_code == 200:
            if response.text != 'null':
                userlist = loads(response.text)
                for i, user in enumerate(userlist):
                    userlist[i] = Simple_User(**user)
                return render_template('client/rol-de-membros.html', userlist=userlist)
            else:
                flash('Algo deu errado')
                return redirect('/painel')    
        else:
            flash('Algo deu errado')
            return redirect('/painel')
    except Exception as error:
        print(str(error))
        flash('Algo deu errado')
        return redirect('/painel')