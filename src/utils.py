import requests
import logging

logger = logging.getLogger("<<< Utils >>>")
logging.basicConfig(level=logging.INFO)

def post(url:str, data:dict, headers:dict=None):
    response = requests.post(url, json=data, headers=headers)
    return response
