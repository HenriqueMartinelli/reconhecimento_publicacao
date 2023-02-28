from flask import Flask, request, jsonify, render_template
import uuid, json
from main import PublicacaoClient, MainClientException
import re

app = Flask(__name__)
client = PublicacaoClient()

@app.route('/', methods=['GET'])
def home():
  return render_template('pagina.html')

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
    # try:
        content = get_content(["key", "value", "publicacao"])
        print(content)
        publicacao, value = client.decode_text(content["publicacao"]), client.decode_text(content["value"])
        resultado = client.update_json(key=content["key"], value=value, publicacao=publicacao)
        if type(resultado) is dict:
            return {
                "sucesso" : True,
                "key": content["key"],
                "value": value,
                "msg": f"Cadastrado. Ocorrencias encontradas: {resultado['total']}",
                "ocorrencias encontradas": resultado['total'],
                "publicacoes": resultado['publicacoes']
            }  

        return {
                "sucesso" : False,
                "key": content["key"],
                "value": value,
                "msg": resultado
            }  


    # except MainClientException as e:
    #     return error(e.args[0])
    # except:
    #     return error() 


# @app.route('/testar', methods=['POST'])
# def testar():
#     try:
#         content = get_content(['key'])
#         resultado = client.teste_novoTermo(key=content["key"])

#         return {
#             "key": content["key"],
#             "ocorrencias encontradas": resultado
#         }  
#     except MainClientException as e:
#         return error(e.args[0])
#     except:
#         return error() 


@app.route('/testartotal/', methods=['GET'])
def testar_total():
    try:
        resultado = client.testar_total()
        return resultado 
    except MainClientException as e:
        return error(e.args[0])
    except:
        return error() 


@app.route('/keys', methods=['GET'])
def chaves():
  with open('utils/termos.json') as f:
    termos = json.load(f)
  chaves = [t.encode('UTF-8').decode() for t in termos.keys()]
  return sorted(chaves)

@app.route('/get_value/<key>', methods=['GET'])
def value(key):
  with open('utils/termos.json') as f:
    termos = json.load(f)
  value = termos.get(key)
  if value:
      return {'value': client.decode_text(value.encode('UTF-8').decode()).upper().replace("\\","").replace('.+','(...)')}
  else:
      return jsonify({'error': 'Chave não encontrada'}), 404

### tem que fazer um endpoint para teste de nova chave
@app.route('/cadastrar_value', methods=['POST'])
def cadastrar_nova_key():
  try:
    content = request.json
    with open('utils/termos.json') as f:
      termos = json.load(f)
    key = content['key']
    texto = content['value']
    print(texto)
    texto = re.escape(texto)
    texto = texto.replace('\\(\\.\\.\\.\\)','.+')
    print(texto)
    termos[key] = termos[key]+'|'+texto
    with open('utils/termos.json','w') as f:
      json.dump(termos, f)
    return {'status':'Ok',
            'resultado': ' foi cadastrado'}
  except:
    return {'status':'Erro',
            'resultado': ' não foi cadastrado'}



@app.route('/teste', methods=['POST'])
def teste():
    try:
        content = request.json
        print(content)
        new_dict = content
        texto = content['key']
        # content = get_content(['key'])
        texto = re.escape(texto)
        texto = texto.replace('\\(\\.\\.\\.\\)','.+')
        new_dict['key'] = texto
        resultado = client.teste_novoTermo(novoTermos=new_dict)
        
        return {
            "key": content,
            # "ocorrencias encontradas": resultado,
            "ocorrencias encontradas": resultado['total'],
            "publicacoes": resultado['publicacoes']
        }  
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