from flask import Flask, request
import uuid
from main import PublicacaoClient

app = Flask(__name__)

#clients = {}
# clients = SharedMemoryDict(name='clients', size=1024)
client = PublicacaoClient()



@app.route('/buscatermos', methods=['POST'])
def buscar():
    try:
        content = get_content(["publicacao"])
        resultado = client.busca_termos(content["publicacao"])
        if resultado:
            dados = client.getattribute(content["publicacao"])
            return {
                    "sucesso" : True,
                    "key" : resultado,
                    "autor": dados.get('autor'),
                    "juiz": dados.get('relator/juiz'),
                    "adv autor": dados.get('adv autor'),
                    'reu': dados.get('reu'),
                    "adv reu": dados.get('adv reu'),
                    'comarca/jurisdição': dados.get('comarca/jurisdição')
                }    
        
        return {
            "sucesso" : False,
            "key": "Não encontrada",
        }    
    # except DetranClientException as e:
    #     return error(e.args[0])
    except Exception as e: 
        print(e)
    except:
        return error() 

@app.route('/update', methods=['POST'])
def atualizar():
    # try:
        # content = get_content(["token"])
        content = get_content(["key", "value", "publicacao"])
        publicacao, value = decode_payload(content['publicacao']), decode_payload(content["value"])
        resultado = client.update_json(key=content["key"], value=value, publicacao=publicacao)
        if type(resultado) is int:
            return {
                "sucesso" : True,
                "key": content["key"],
                "value": value,
                "msg": "Cadastrado",
                "ocorrencias encontradas": resultado
            }  

        return {
                "sucesso" : False,
                "key": content["key"],
                "value": content["value"],
                "msg": resultado
            }  


        # client = get_client(content)
        # clients = SharedMemoryDict(name='clients', size=1024)
        # del clients[content["token"]]
    #     return ok()
    # except DetranClientException as e:
    #     return error(e.args[0])
    # except Exception as e: 
    #     print(e)
    # except:
    #     return error() 

@app.route('/testar', methods=['POST'])
def testar():
    try:
        content = get_content(["key"])
        resultado = client.teste_novoTermo(content["key"])
        return {
            "key": content["key"],
            "ocorrencias encontradas": resultado
        }  
    # except DetranClientException as e:
    #     return error(e.args[0])
    except Exception as e: 
        print(e)
    except:
        return error() 

        
###################################################################
#   Utils
###################################################################


def get_content(required_fields):
    content = request.form
    validate_content(content, required_fields)
    return content

def validate_content(content, required_fields):
    for field in required_fields:
        if field not in content:
            print("Requisição inválida.")

def error(msg="Erro desconhecido ao processar requisição."):
    return {
        "sucesso" : False,
        "msg": msg
    }

def decode_payload(content):
    str_bytes = bytes(content,'UTF-8')
    str_bytes = str_bytes.decode('unicode_escape').encode('raw_unicode_escape')
    return str_bytes.decode()
            

def invalid_request():
    return error("Requisição inválida.")

def ok():
    return {
        "sucesso" : True
    }