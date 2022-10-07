from flask import redirect, render_template, flash
from flask_login import current_user

def admin_permission(func):
    '''
    Permite que apenas usuários com is_admin == True tenham acesso ao
    endpoint.
    '''
    def admin_check(*args, **kwargs):
        try:
            if current_user.is_admin == False:
                return redirect('/painel')
        except AttributeError:
            return redirect('/entrar')
        except:
            flash('Erro Inesperado')
            return redirect('/painel')
        return func(*args, **kwargs)
    admin_check.__name__ = func.__name__
    return admin_check


def treasurer_permission(func):
    '''
    Permite que apenas usuários com is_treasurer == True tenham acesso ao
    endpoint.
    '''
    def treasurer_check(*args, **kwargs):
        try:
            if current_user.is_treasurer == False:
                return redirect('/painel')
        except AttributeError as error:
            return redirect('/entrar')
        except:
            flash('Erro Inesperado')
            return redirect('/painel')
        return func(*args, **kwargs)
    treasurer_check.__name__ = func.__name__
    return treasurer_check


def secretary_permission(func):
    '''
    Permite que apenas usuários com is_secretary == True tenham acesso ao
    endpoint.
    '''
    def secretary_check(*args, **kwargs):
        try:
            if current_user.is_secretary == False:
                return redirect('/painel')
        except AttributeError:
            return redirect('/entrar')
        except:
            flash('Erro Inesperado')
            return redirect('/painel')
        return func(*args, **kwargs)
    secretary_check.__name__ = func.__name__
    return secretary_check


def designer_kick(func):
    '''
    Proíbe o acesso da página por designers
    '''
    def designer_check(*args, **kwargs):
        try:
            if current_user.is_designer == True:
                return redirect('/home')
        except AttributeError:
            return redirect('/entrar')
        except:
            flash('Erro Inesperado')
            return redirect('/home')
        print(args, kwargs)
        return func(*args, **kwargs)
    designer_check.__name__ = func.__name__
    return designer_check

def all_admin_permission(func):
    '''
    Permite que todos os usuários com senha administrativa (exceto designers) tenham acesso ao endpoint
    '''
    def all_admin_check(*args, **kwargs):
        try:
            if current_user.is_admin or current_user.is_treasurer or current_user.is_secretary or current_user.is_adviser:
                return func(*args, **kwargs)
            elif current_user.is_designer == True:
                return redirect('/home')
            else:
                # Evita o loop infinito de redirecionamentos
                if func.__name__ == 'painel':
                    return func(*args, **kwargs)
                else:
                    return redirect('/painel')
        except AttributeError:
            return redirect('/entrar')
        except Exception as error:
            if current_user.is_designer == True:
                return redirect('/home')
            flash('Erro Inesperado')
            print(str(error))
            return redirect('/painel')
    all_admin_check.__name__ = func.__name__
    return all_admin_check