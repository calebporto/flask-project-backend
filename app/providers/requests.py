import requests
import os

API_URL = os.environ["API_URL"]
API_KEY = os.environ["API_KEY"]
AUTHORIZED_IP = os.environ["AUTHORIZED_IP"]
headers = {'api_key': API_KEY, 'id': AUTHORIZED_IP}

def post_request(endpoint, data):
    return requests.post(f'{API_URL}{endpoint}', data, headers=headers)

def get_request(endpoint):
    return requests.get(f'{API_URL}{endpoint}', headers=headers)

def delete_request(endpoint):
    return requests.delete(f'{API_URL}{endpoint}', headers=headers)