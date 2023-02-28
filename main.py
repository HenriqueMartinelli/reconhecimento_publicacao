import json 
import pandas as pd
import re
import traceback
from utils.pattern import extract

class MainClientException(Exception):
    pass


class PublicacaoClient:
    def __init__(self):
        self.termosPadrao = self.load_termos("utils/termos")

    ## FAZ A BUSCA DO TERMO ENCIMA DA PUBLICACAO FORNECIDA
    def busca_termos(self, publicacao:str, termos=None):
        if termos is None: termos = self.termosPadrao
        for key, value in termos.items():
            value =  self.decode_text(value)
            r = re.search(re.compile(value.lower()), publicacao.lower())
            if r:
                return key
        return False


    def update_json(self, key:str, value:str, publicacao:str):
        novoTermo = {key : self.decode_text(value)}
        ## REGRA DE VERIFICACAO 
        if not self.verificar_keys(key): 
            return "Key já Cadastrada."
        if not self.verificar_value(publicacao=publicacao, novoTermo=novoTermo):
            return "Termo não encontrado na publicação informada."
        ## SALVAR ##
        resultado = self.teste_novoTermo(novoTermos=novoTermo)
        self.termosPadrao.update(novoTermo)

        if resultado['total'] > 10:
            self.save_json(self.termosPadrao)
        return resultado

    ## VERIFICA SE NAO EXISTE UMA KEY DO JSON COM O MESMO NOME
    def verificar_keys(self, key:str):
        if key in self.termosPadrao.keys():
            return False
        return True

    ## VERIFICA SE TERMO JÁ NÃO FOI CADASTRADO NO JSON PADRAO
    def verificar_value(self, publicacao:str, novoTermo:dict):
        if self.busca_termos(publicacao=publicacao, termos=novoTermo):
            return True
        return False

    
    ## TESTA O NOVO TERMO CADASTRADO E RETORNA OS MATCH
    def teste_novoTermo(self, key=None, novoTermos=None):
        if type(novoTermos) is not dict:
            if self.verificar_keys(key): 
                return "Key não cadastrada."
            novoTermos = {key: self.termosPadrao.get(key)}

        df = self.publicacao_padrao()
        total = 0
        result_publicacao = list()
        for _, row in df.iterrows():
            resultado = self.busca_termos(publicacao=self.decode_text(row['teor']), termos=novoTermos)
            if resultado:
                total += 1
                if len(result_publicacao) < 20:
                    result_publicacao.append(row['teor'])

        return {
            "total": total,
            "publicacoes": result_publicacao
        }

    ## TESTA TODOS OS TERMOS JÁ CADASTRADOS COM O BANCO DE TESTE EXCEL
    def testar_total(self):
        df = self.publicacao_padrao()
        termos = self.termosPadrao

        total = 0
        _json = dict()
        for key, value in termos.items():
            atual  = 0
            for index, row in df.iterrows():
                publicacao, value = self.decode_text(row['teor']), self.decode_text(value)
                r = re.search(re.compile(value.lower()), publicacao.lower())
                if r: 
                    atual += 1
                    total += 1

            _json.update({key: atual})
        _json.update({'total': total})
        return _json

    ## CARREGA O BANCO PADRAO DE TESTE DE 70000 LINHAS DE PUBLICACAO
    def publicacao_padrao(self):
        return pd.read_excel("utils/decisao.xlsx")

    ## CARREGA JSON COM O TERMOS JÁ SALVOS
    def load_termos(self, arquivo):
      with open(arquivo + ".json") as f:  
        termos = json.load(f)
      return termos


    def save_json(self, dict):
        with open('utils/termos.json', 'w') as fp:
            json.dump(dict, fp)

    ## FAZ O DECODE DA PUBLICACAO E O TERMO
    def decode_text(self, texto):
        try:
            texto_decode = texto.encode("ISO-8859-1").decode("utf-8")
            texto_bytes = bytes(texto_decode,'UTF-8')
            texto_convertido = texto_bytes.decode('unicode_escape').encode('raw_unicode_escape')
            return texto_convertido.decode('utf-8')
        except: 
            return texto

    ## EXTRAI OS ATRIBUTOS APÓS CONFIRMA O MATCH DA PUBLICACAO
    def extrair_atributos(self, text):
        try:
            dado = self.decode_text(text)
            primeiros_termos = dado[:100]
            Getextract = extract()
            if 'intimação' in dado[:20].lower() or 'ato ordinatório' in dado[:20].lower():
                try:
                    dados =  Getextract.extrair_intimacao_1(dado)
                except: 
                    dados =  Getextract.extrair_intimacao_2(dado)
            elif 'PUBLICAÇÃO DE ACÓRDÃOS' in primeiros_termos or 'AGRAVO INTERNO' in primeiros_termos.upper() or 'MANDADO DE SEGURANCA' in primeiros_termos.upper():
                dados =  Getextract.extrair_agravo(dado)
            else:
                dados = Getextract.extrair_decisao(dado)
            return dados
        except:
            return False