from flask import redirect, render_template, request, flash
from app.providers.hash_provider import get_password_hash
from flask_login import login_required, current_user
from app.models.basemodels import User_With_Data
from http.client import HTTPException
from app.models.basemodels import *
from datetime import datetime, date
from app.config import API_URL
from json import loads
from app import app
import requests
import json


@app.route('/painel-administrativo/')
@login_required
def painel_administrativo():
    try:
        if current_user.is_admin == False:
            return redirect('/painel')
    except AttributeError:
        return render_template('client/entrar.html')
    except:
        return 'Erro Inesperado'

    waiting_query = requests.get(f'{API_URL}/waiting-list')
    waiting_list_size = len(loads(waiting_query.text))

    return render_template('admin/painel-administrativo.html', waiting_list_size=waiting_list_size)

@app.route('/painel-administrativo/entradas', methods=['GET', 'POST'])
@login_required
def entradas():
    try:
        if current_user.is_admin == False:
            return redirect('/painel')
    except AttributeError:
        return render_template('client/entrar.html')
    except:
        return 'Erro Inesperado'

    if request.method == 'POST':
        try:
            treasurer_id = int(request.form.get('treasurer_id'))
            if not request.form.get('json'):
                flash('Você deve registrar pelo menos um dízimo ou uma oferta.')
                return redirect('/painel-administrativo/entradas')
            data = loads(request.form.get('json'))
            tithes = []
            offers = []
            for key, value in data.items():
                if value['tipo'] == 'dizimo':
                    tithe_date = datetime.strptime(value['data'], '%d/%m/%Y').date()
                    if tithe_date.month != (date.today()).month:
                        flash('O mês da entrada não pode ser diferente do atual.')
                        return redirect('/painel-administrativo/entradas')
                    elif date.today() < tithe_date:
                        flash('Você não pode inserir uma data maior que a atual.')
                        return redirect('/painel-administrativo/entradas')
                    elif (date.today()).year != tithe_date.year:
                        flash('O ano da entrada não pode ser diferente do atual.')
                        return redirect('/painel-administrativo/entradas')
                    elif tithe_date.day > 31 or tithe_date.day < 1:
                        flash('Data inválida. Verifique os dados.')
                        return redirect('/painel-administrativo/entradas')
                    
                    tithe_date_str = tithe_date.strftime('%Y-%m-%d')
                    tithe_dict = {
                        'user_id': int(value['id']), 
                        'value': float(value['valor']),
                        'tithe_date': tithe_date_str,
                        'treasurer_id':treasurer_id
                        } 
                    tithes.append(tithe_dict)
                else:
                    offer_date = datetime.strptime(value['data'], '%d/%m/%Y').date()
                    if offer_date.month != (date.today()).month:
                        flash('O mês da entrada não pode ser diferente do atual.')
                        return redirect('/painel-administrativo/entradas')
                    elif date.today() < offer_date:
                        flash('Você não pode inserir uma data maior que a atual.')
                        return redirect('/painel-administrativo/entradas')
                    elif (date.today()).year != offer_date.year:
                        flash('O ano da entrada não pode ser diferente do atual.')
                        return redirect('/painel-administrativo/entradas')
                    elif offer_date.day > 31 or offer_date.day < 1:
                        flash('Data inválida. Verifique os dados.')
                        return redirect('/painel-administrativo/entradas')
                    offer_date_str = offer_date.strftime('%Y-%m-%d')
                    offer_dict = {
                        'value': float(value['valor']),
                        'offer_date': offer_date_str,
                        'treasurer_id': treasurer_id
                        }
                    offers.append(offer_dict)

            if len(tithes) > 0:
                tithe_response = requests.post(f'{API_URL}/tithe-include', json.dumps(tithes))
                if tithe_response.status_code == 200:
                    pass
                else:
                    flash('Algo deu errado na inclusão dos dízimos. Confira os dados fornecidos.')
            
            if len(offers) > 0:
                print(json.dumps(offers))
                offer_response = requests.post(f'{API_URL}/offer-include', json.dumps(offers))
                if offer_response.status_code == 200:
                    pass
                else:
                    flash('Algo deu errado na inclusão das ofertas. Confira os dados fornecidos')
            
            flash('Dados registrados com sucesso.')
            return redirect('/painel-administrativo')
        except:
            flash('Algo deu errado.Tente novamente.')
            return redirect('/painel-administrativo/entradas')
    else:
        try:
            response = requests.get(f'{API_URL}/user-list')
            if response.status_code == 200:
                userlist = loads(response.text)
                for i, user in enumerate(userlist):
                    userlist[i] = Simple_User(**user)
                return render_template('admin/entradas.html', userlist=userlist)
            else:
                flash('Algo deu errado.')
                return redirect('/painel-administrativo')
        except Exception as error:
            return HTTPException(400, detail=str(error))

@app.route('/painel-administrativo/saidas', methods=['GET', 'POST'])
@login_required
def saidas():
    try:
        if current_user.is_admin == False:
            return redirect('/painel')
    except AttributeError:
        return render_template('client/entrar.html')
    except:
        return 'Erro Inesperado'
    
    if request.method == 'POST':
        try:
            request_value = request.form.get('valor').replace('.', '')
            value = float(request_value.replace(',', '.'))
            expense_date = datetime.strptime(request.form.get('data'), '%d/%m/%Y').date()
            treasurer_id = int(request.form.get('treasurer_id'))
            
            if value <= 0:
                flash('Insira um valor válido')
                return redirect('/painel-administrativo/saidas')
            elif expense_date.month != date.today().month or expense_date.year != date.today().year:
                flash('O registro deve ser do mês atual')
                return redirect('/painel-administrativo/saidas')
            elif expense_date > date.today():
                flash('Data inválida.')
                return redirect('/painel-administrativo/saidas')
            
            send = Expense(
                value=value,
                description=(request.form.get('descricao')).lower(),
                expense_date=expense_date,
                treasurer_id=treasurer_id
            )
            response = requests.post(f'{API_URL}/expense-include', send.json())
            if response.status_code == 200:
                flash('Saída registrada com sucesso.')
                return redirect('/painel-administrativo/saidas')
            else:
                flash('Algo deu errado, tente novamente mais tarde.')
                return redirect('/painel-administrativo/saidas')
        except:
            flash('Algo deu errado, tente novamente mais tarde.')
            return redirect('/painel-administrativo/saidas')
    else:
        return render_template('admin/saidas.html')

@app.route('/painel-administrativo/historico-de-dizimos')
@login_required
def historico_de_dizimos():
    try:
        if current_user.is_admin == False:
            return redirect('/painel')
    except AttributeError:
        return render_template('client/entrar.html')
    except:
        return 'Erro Inesperado'

    periodo_select = '-- Mês atual --'

    if request.args.get('time'):
        tithe_time = int(request.args.get('time'))
        response = requests.get(f'{API_URL}/tithe-list/{tithe_time}/{-1}/1')
        print(tithe_time)
        match tithe_time:
            case 30:
                periodo_select = '-- 30 dias --'
            case 60:
                periodo_select = '-- 60 dias --'
            case 180:
                periodo_select = '-- 6 meses --'
                print(periodo_select)
            case 365:
                periodo_select = '-- 1 ano --'
    else:
        current_month_days = date.today().day
        response = requests.get(f'{API_URL}/tithe-list/{current_month_days}/{-1}/1')

    tithe_list = loads(response.text)['tithe_list']
    for i, item in enumerate(tithe_list):

        tithe_date = (datetime.strptime(item['tithe_date'], '%Y-%m-%d')).strftime('%d/%m/%Y')
        name = item['username'].title()
        value = item['value']
        value2 = (f'R$ {value:,.2f}').replace(".", ",")
        tithe = History_Tithe(
            tithe_date=tithe_date,
            name= name,
            value= value2
        )
        tithe_list[i] = tithe

    return render_template('admin/historico-de-dizimos.html', tithe_list=tithe_list, periodo_select=periodo_select)


@app.route('/painel-administrativo/lista-de-membros')
@login_required
def lista_de_membros():
    try:
        if current_user.is_admin == False:
            return redirect('/painel')
    except AttributeError:
        return render_template('client/entrar.html')
    except:
        return 'Erro Inesperado'
    try:
        response = requests.get(f'{API_URL}/user-list')
        if response.status_code == 200:
            userlist = loads(response.text)
            for i, user in enumerate(userlist):
                userlist[i] = Simple_User(**user)
            return render_template('admin/lista-de-membros.html', userlist=userlist)
        else:
            flash('Algo deu errado')
            return redirect('/painel-administrativo')
    except Exception as error:
        return HTTPException(400, detail=str(error))

@app.route('/painel-administrativo/lista-de-membros/detalhes')
@login_required
def detalhes():
    try:
        if current_user.is_admin == False:
            return redirect('/painel')
    except AttributeError:
        return render_template('client/entrar.html')
    except:
        return 'Erro Inesperado'
    
    try:
        response = requests.get(f'{API_URL}/get-user-with-data/{int(request.args.get("user_id"))}')
        if response.status_code == 200:
            if response.text:
                user_data = User_With_Data(**loads(response.text))
                if user_data.gender.lower() == 'f':
                    user_data.gender = 'Feminino'
                elif user_data.gender.lower() == 'm':
                    user_data.gender = 'Masculino'
                user_data.birth = user_data.birth = (user_data.birth).strftime('%d/%m/%Y')
                
                return render_template('admin/detalhes.html', user_data=user_data)
            else:
                flash('Não foi possível efetuar a solicitação.')
                return redirect('/painel-administrativo')
        else:
            flash('Algo deu errado.')
            return redirect('/painel-administrativo')
    except:
        flash('Algo deu errado.')
        return redirect('/painel-administrativo')

@app.route('/painel-administrativo/lista-de-espera', methods=['GET', 'POST'])
@login_required
def lista_de_espera():
    try:
        if current_user.is_admin == False:
            return redirect('/painel')
    except AttributeError:
        return render_template('client/entrar.html')
    except:
        return 'Erro Inesperado'
    if request.method == 'POST':
        if request.form.get('action') == 'accept':
            send = Add_User(
                user=UserAdd(
                    user_to_del=int(request.form.get('user_to_del')),
                    name=request.form.get('name'),
                    email=request.form.get('email'),
                    hash=request.form.get('hash'),
                    is_admin=False,
                    is_designer=False
                ), user_data=User_Data(
                    cep=request.form.get('cep'),
                    address=request.form.get('address'),
                    gender=request.form.get('gender'),
                    tel=request.form.get('tel'),
                    birth=datetime.strptime(request.form.get('birth'), '%d/%m/%Y').date(),
                    added=date.today()
                )
            )
            accept = requests.post(f'{API_URL}/add-user', send.json())
            if accept.status_code == 200:
                flash('Cadastro registrado com sucesso.')
                return redirect('/painel-administrativo/lista-de-espera')
            else:
                flash('Não foi possível efetuar a solicitação.')
                return redirect('/painel-administrativo/lista-de-espera')
        else:
            reject = requests.delete(f'{API_URL}/reject-waiting-user/{int(request.form.get("id"))}')
            if reject.status_code == 200:
                flash('Cadastro rejeitado.')
                return redirect('/painel-administrativo/lista-de-espera')
            else:
                flash('Não foi possível efetuar a solicitação.')
                return redirect('/painel-administrativo/lista-de-espera')
    else:
        try:
            if current_user.is_admin == False:
                return redirect('/painel')
        except AttributeError:
            return render_template('client/entrar.html')
        except:
            return 'Erro Inesperado'

        waiting_query = requests.get(f'{API_URL}/waiting-list')
        waiting_list = loads(waiting_query.text)
        for i, pessoa in enumerate(waiting_list):
            waiting_list[i] = User_With_Data(**pessoa)
            if (waiting_list[i].gender).lower() == 'm':
                waiting_list[i].gender = 'Masculino'
            elif (waiting_list[i].gender).lower() == 'f':
                waiting_list[i].gender = 'Feminino'
            waiting_list[i].birth = (waiting_list[i].birth).strftime('%d/%m/%Y')
            waiting_list[i].name = (waiting_list[i].name).title()
            waiting_list[i].address = (waiting_list[i].address).title()

        return render_template('admin/lista-de-espera.html', waiting_list=waiting_list)

@app.route('/painel-administrativo/adicionar-membro', methods=['GET', 'POST'])
@login_required
def adicionar_membro():
    try:
        if current_user.is_admin == False:
            return redirect('/painel')
    except AttributeError:
        return render_template('client/entrar.html')
    except:
        return render_template('client/entrar.html')

    if request.method == 'POST':
        address = f'{request.form.get("logradouro")} {request.form.get("numero")}, {request.form.get("bairro")}, {request.form.get("cidade")} - {request.form.get("uf")}'
        senha = get_password_hash(request.form.get('senha'))
        send = Add_User(
            user=UserAdd(
                name= request.form.get('nome').lower(), 
                email= request.form.get('email').lower(), 
                hash= senha
            ), user_data= User_Data(
                cep= request.form.get('cep').lower(), 
                address= address.lower(), 
                gender = request.form.get('sexo').lower(),
                tel= request.form.get('tel').lower(), 
                birth= datetime.strptime(request.form.get('nascimento'), '%d/%m/%Y').date()),
                added= date.today()
            )

        response = requests.post(f'{API_URL}/add-user', send.json())
        
        if response.status_code == 200:
            dados = loads(response.text)['confirm']

            if dados == False:
                flash('E-mail já cadastrado.')
                return redirect('/painel-administrativo')
            else:
                flash('Cadastro realizado com sucesso')
                return redirect('/painel-administrativo')
        else:
            flash('Algo deu errado. Tente novamente mais tarde.')
            return redirect('/painel-administrativo')
    else:
        return render_template('admin/adicionar-membro.html')

@app.route('/painel-administrativo/alterar-cadastro', methods=['GET', 'POST'])
@login_required
def alterar_cadastro():
    try:
        if current_user.is_admin == False:
            return redirect('/painel')
    except AttributeError:
        return render_template('client/entrar.html')
    except:
        return render_template('client/entrar.html')
    if request.method == 'POST':
        send = User_Update(
            id = request.form.get('selecionar'),
            name = request.form.get('nome'),
            email = request.form.get('email'),
            cep = request.form.get('cep'),
            address = request.form.get('endereco'),
            gender = request.form.get('sexo'),
            tel = request.form.get('celular'),
            birth = datetime.strptime(request.form.get('nascimento'), '%d/%m/%Y').date()
        )
        response = requests.post(f'{API_URL}/user-update', send.json())
        if response.status_code == 200:
            flash('Cadastro alterado com sucesso.')
            return redirect('/painel-administrativo')
        else:
            flash('Erro na solicitação.')
            return redirect('/painel_administrativo')
    else:
        try:
            response = requests.get(f'{API_URL}/user-list')
            if response.status_code == 200:
                userlist = loads(response.text)
                for i, user in enumerate(userlist):
                    userlist[i] = Simple_User(**user)
                return render_template('admin/alterar-cadastro.html', userlist=userlist)
        except Exception as error:
            return HTTPException(400, detail=str(error))

@app.route('/get-user-data/<user_id>') # Api para Ajax
@login_required
def get_user_data(user_id):
    try:
        user = requests.get(f'{API_URL}/get-user-with-data/{int(user_id)}')
    
        if user.status_code == 200:
            userdata = loads(user.text)
            birth = datetime.strptime(userdata['birth'], '%Y-%m-%d').date()
            userdata['birth'] = birth.strftime('%d/%m/%Y')
            return json.dumps(userdata)
        return None
    except Exception as error:
        return HTTPException(400, detail=str(error))

@app.route('/painel-administrativo/excluir-membro', methods=['GET', 'POST'])
@login_required
def excluir_membro():
    try:
        if current_user.is_admin == False:
            return redirect('/painel')
    except AttributeError:
        return render_template('client/entrar.html')
    except:
        return render_template('client/entrar.html')
    
    if request.method == 'POST':
        response = requests.delete(f'{API_URL}/delete-user/{int(request.form.get("user_id"))}')
        if response.status_code == 200:
            if loads(response.text)['confirm'] == True:
                flash('Membro excluído com sucesso')
                return redirect('/painel-administrativo')
            else:
                flash('Não foi possível efetuar a solicitação.')
                return redirect('/painel-administrativo')
        else:
            flash('Algo deu errado.')
            return redirect('/painel-administrativo')
    else:
        try:
            response = requests.get(f'{API_URL}/user-list')
            if response.status_code == 200:
                userlist = loads(response.text)
                for i, user in enumerate(userlist):
                    userlist[i] = Simple_User(**user)
                return render_template('admin/excluir-membro.html', userlist=userlist)
        except Exception as error:
            return HTTPException(400, detail=str(error))
        