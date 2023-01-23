import json 
import pandas as pd
import re
import traceback

class PublicacaoClient:
    def __init__(self):
        self.termosPadrao = self.load_termos("termos")

    def busca_termos(self, publicacao:str, termos=None):
        if termos is None: termos = self.termosPadrao
        for key, value in termos.items():
            publicacao, value = self.decode_text(publicacao), self.decode_text(value)
            r = re.search(re.compile(value.lower()), publicacao.lower())
            if r:
                return key
        return False

    def update_json(self, key:str, value:str, publicacao:str):
        novoTermo = {key : value}
        ## REGRA DE VERIFICACAO 
        if not self.verificar_keys(key): 
            return "Key já Cadastrada."
        if not self.verificar_value(publicacao=publicacao, novoTermo=novoTermo):
            return "Termo não encontrado na publicação informada."
        ## SALVAR ##
        resultado = self.teste_novoTermo(novoTermos=novoTermo)
        return resultado


    def verificar_keys(self, key:str):
        if key in self.termosPadrao.keys():
            return False
        return True

    def verificar_value(self, publicacao:str, novoTermo:dict):
        if self.busca_termos(publicacao=publicacao, termos=novoTermo):
            return True
        return False

    
    def teste_novoTermo(self, novoTermos=None):
        # if type(novoTermos)is dict:
        #     novoTermos = {novoTermos: self.termosPadrao.get(novoTermos)}
        # novoTermos = self.termosPadrao

        total = 0
        df = self.publicacao_padrao()
        for index, row in df.iterrows():
            resultado = self.busca_termos(publicacao=row['teor'], termos=novoTermos)
            if resultado:
                total += 1

        # total = 0
        # df = self.publicacao_padrao()
        # for key, value in novoTermos.items():
        #     atual  = 0
        #     for index, row in df.iterrows():
        #         publicacao, value = self.decode_text(row['teor']), self.decode_text(value)
        #         r = re.search(re.compile(value.lower()), publicacao.lower())
        #         if r:
        #             atual += 1
        #             total += 1
        #     print(f"contagem:{atual}, {value}")
            
        return total

    def publicacao_padrao(self):
        return pd.read_excel("decisao.xlsx")

    def load_termos(self, arquivo):
        f = open(arquivo + ".json")
        termos = json.load(f)
        return termos

    def decode_text(self, texto):
        try:
            texto_decode = texto.encode("ISO-8859-1").decode("utf-8")
            texto_bytes = bytes(texto_decode,'UTF-8')
            texto_convertido = texto_bytes.decode('unicode_escape').encode('raw_unicode_escape')
            return texto_convertido.decode('utf-8')
        except: 
            return texto

    def getattribute(self, texto):
        try:

            texto = self.decode_text(texto=texto)
            print(texto)
            dados = dict()
            pattern_autor = re.compile('autor: |agravante: |reclamante: |recorrente: |impetrante: ',re.IGNORECASE)
            pattern_reu = re.compile('réu: |agravado: |reclamado: |reclamado (a): |recorrido: |impetrado: ', re.IGNORECASE)
            pattern_advogados = re.compile('advogado|advogada',re.IGNORECASE)
            pattern_decisao = re.compile('relator: |decisão: |decisao: |despacho |ATO ORDINATÓRIO NA', flags=re.IGNORECASE or re.MULTILINE)
            pattern_jurisdicao = re.compile('jurisdicao: |jurisdição: |comarca: ',re.IGNORECASE)
            pattern_juiz_relator = re.compile('relator: |',re.IGNORECASE)

            corte_final = re.search(pattern_decisao, texto).span()[0]
            corte_jurisdicao = re.search(pattern_jurisdicao, texto).span()[0]
            idx_inicio_autor = re.search(pattern_autor, texto).span()[0]
            idx_inicio_reu = re.search(pattern_reu, texto).span()[0]


            if idx_inicio_autor < idx_inicio_reu:
                corte_inicial = idx_inicio_autor
                inicial = 'autor'
            else:
                corte_inicial = idx_inicio_reu
                inicial = 'reu'

            cabecalho = texto[corte_inicial:corte_final]

            parte_autor = cabecalho[:re.search(pattern_reu, cabecalho).span()[0]]
            parte_reu = cabecalho[re.search(pattern_reu, cabecalho).span()[0]:]
            autor = parte_autor.split('Advogado: ')[0]
            advogados_autor = ''.join(parte_autor.split('Advogado: ')[1:])
            reu = parte_reu.split('Advogado: ')[0]
            advogados_reu = ''.join(parte_reu.split('Advogado: ')[1:])
            comarca = texto[corte_jurisdicao:corte_inicial]
            relator = texto[texto.find('Relator: '):corte_final]

            dados['autor'] = re.sub(pattern_autor,'',autor)
            dados['adv autor'] = advogados_autor
            dados['reu'] = re.sub(pattern_reu,'',reu)
            dados['adv reu'] = advogados_reu
            dados['comarca/jurisdição'] = re.sub(pattern_jurisdicao,'',comarca)
            dados['relator/juiz'] = relator
            return dados
        except:
            print(traceback.format_exc())