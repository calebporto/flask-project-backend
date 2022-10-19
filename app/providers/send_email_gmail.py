import smtplib
import email.message

import os

def redefinir_senha_email(receiver_list, subject, token):
    '''
    Receiver_list: tupla com os destinatários
    Subject: Assunto do email
    Message: Corpo do e-mail
    '''

    email_body = f'''
    <div style="width: 70%; margin: auto;">
        <div style= "
        text-align: center;
        width: 100%;
        background: linear-gradient(rgb(82, 8, 8), black);
        padding: 20px;
        border-radius: 10px;">
            <p style="font-size: 30px; margin-bottom: 30px; font-weight: bold; color: #fff;">Igreja Batista Village Guaxindiba</p>
            <p style="font-weight: bold; font-size: 12px; color: #fff;">REDEFINIÇÃO DE SENHA</p>
        </div>
        <div style="padding: 10px; margin-top: 20px; color: black;">
            <p style="font-size: 15px;">Para redefinir sua senha, clique no botão abaixo:</p>
        </div>
        <div style="padding: 10px; margin: auto; margin-top: 20px; color: black;">
            <a href="{os.environ['APP_URL']}/recuperar-senha/nova-senha?id={token}" style="margin: auto; width: 100%; text-align: center;">
                <button style="
                cursor: pointer;
                font-size: 20px;
                font-weight: bold;
                width: 30%;
                padding: 15px;
                border: none;
                border-radius: 10px;
                color: black;
                background: linear-gradient(rgb(219, 243, 112), rgb(133, 131, 0));
                margin: auto;">
                Redefinir Senha
                </button>
            </a>
        </div>
    </div>
    '''

    msg = email.message.Message()
    msg['Subject'] = subject
    msg['From'] = os.environ['EMAIL_ACCOUNT']
    msg['To'] = receiver_list
    password = os.environ['EMAIL_PASSWORD']
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(email_body)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], msg['To'], msg.as_string().encode('utf-8'))

    print('email enviado')
