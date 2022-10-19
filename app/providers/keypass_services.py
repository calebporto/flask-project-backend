from secrets import token_urlsafe


'''
Keypass é a chave gerada para redefinir a senha do usuário.
Um token é gerado e passado na url enviada por e-mail para o cliente,
que ao ser acessada autoriza a alteração da senha.
'''

def keypass_generator():
    keypass = token_urlsafe(36)
    return keypass