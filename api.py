from flask import Flask, request
import uuid
from main import PublicacaoClient, MainClientException
import chardet
app = Flask(__name__)
client = PublicacaoClient()

@app.route('/buscatermos', methods=['POST'])
def buscar():
    try:
        content = get_content(["publicacao"])
        publicacao = client.decode_text(content['publicacao'])
        resultado = client.busca_termos(publicacao=publicacao)
        if resultado:
            dados = client.extrair_atributos(text=publicacao)
            if type(dados) is dict: 
                return {
                        "sucesso" : True,
                        "key" : resultado,
                        "processo": dados.get('processo'),
                        "autor": dados.get('autor'),
                        "advogados autor": dados.get('advogados_autor'),
                        'reu': dados.get('reu'),
                        "advogado reu": dados.get('advogados_reu'),
                        'comarca/jurisdição': dados.get('comarca')
                    }    

            else:
                return {
                        "sucesso" : True,
                        "key" : resultado,
                        "msg": 'Não foi possivel extrair os dados' 
                        }

        return {
            "sucesso" : False,
            "key": "Não encontrada",
        }    
    except MainClientException as e:
        return error(e.args[0])
    except:
        return error() 
        

@app.route('/update', methods=['POST'])
def atualizar():
    try:
        content = get_content(["key", "value", "publicacao"])
        publicacao, value = client.decode_text(content["publicacao"]), client.decode_text(content["value"])
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
                "value": value,
                "msg": resultado
            }  


    except MainClientException as e:
        return error(e.args[0])
    except:
        return error() 


@app.route('/testar', methods=['POST'])
def testar():
    try:
        content = get_content(['key'])
        resultado = client.teste_novoTermo(key=content["key"])

        return {
            "key": content["key"],
            "ocorrencias encontradas": resultado
        }  
    except MainClientException as e:
        return error(e.args[0])
    except:
        return error() 


@app.route('/testartotal/', methods=['GET'])
def testar_total():
    try:
        resultado = client.testar_total()
        return resultado 
    except MainClientException as e:
        return error(e.args[0])
    except:
        return error() 
        
###################################################################
#   Utils
###################################################################


def get_content(required_fields):
    content = request.json
    validate_content(content, required_fields)
    return content

def validate_content(content, required_fields):
    for field in required_fields:
        if field not in content:
            raise MainClientException("Requisição inválida.")

def error(msg="Erro desconhecido ao processar requisição."):
    return {
        "sucesso" : False,
        "msg": msg
    }
            

def invalid_request():
    return error(msg="Requisição inválida.")

def ok():
    return {
        "sucesso" : True
    }