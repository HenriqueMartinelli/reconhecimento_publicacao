import re
class extract:
    pattern_autor = re.compile('Reclamante: AUTOR: |autor: |agravante: |reclamante: |recorrente: |recorrente:\n|impetrante: ',re.IGNORECASE)
    pattern_reu = re.compile('Reclamado \(a\): RÉU: |réu: |reu: |agravado: |reclamado: |reclamado \(a\): |recorrido: |recorrido:\n|impetrado: ', re.IGNORECASE)
    pattern_advogados = re.compile('advogado|advogada|representante:',re.IGNORECASE)
    pattern_decisao = re.compile('relator: | decisão: | decisao: |despacho |intimação: |\) intimacao: |vistos\.|acórdão|acordao|acordão| Ato Ordinatório |Na forma do Provimento', re.IGNORECASE)
    pattern_juiz_relator = re.compile('relator: |',re.IGNORECASE)
    pattern_processo = re.compile("\d{7}[\-|\.]?\d{2}[\-|\.]?\d{4}[\-|\.]?\d[\-|\.]?\d{2}[\-|\.]?\d{4}")
    pattern_jurisdicao = re.compile('jurisdicao: |jurisdição: |comarca: ',re.IGNORECASE)


    def __init__(self):
        pass

    def remover_dados(self, text):
        sub = ''
        return(re.sub(extract.pattern_advogados,sub,re.sub(extract.pattern_autor,sub,re.sub(extract.pattern_reu,sub,text))))

            
    def extrair_agravo(self, dado):
        retorno = dict()
        corte_inicial = re.search(extract.pattern_processo, dado).span()[1]
        dado = dado[corte_inicial:]
        corte_final = re.search(extract.pattern_decisao, dado).span()[0]
        corte_jurisdicao = re.search(extract.pattern_jurisdicao, dado).span()[0]
        idx_inicio_autor = re.search(extract.pattern_autor, dado).span()[0]
        idx_inicio_reu = re.search(extract.pattern_reu, dado).span()[0]


        if idx_inicio_autor < idx_inicio_reu:
            corte_inicial = idx_inicio_autor
            inicial = 'autor'
        else:
            corte_inicial = idx_inicio_reu
            inicial = 'reu'

        cabecalho = dado[corte_inicial:corte_final]

            
        parte_autor = cabecalho[re.search(extract.pattern_autor, cabecalho).span()[0]:re.search(extract.pattern_reu, cabecalho).span()[0]]
        parte_reu = cabecalho[re.search(extract.pattern_reu, cabecalho).span()[0]:]
        retorno['processo'] = re.search(extract.pattern_processo, dado).group()
        retorno['autor'] = re.sub(extract.pattern_autor,'',parte_autor.split('Advogado: ')[0])
        retorno['advogados_autor'] = ''.join(parte_autor.split('Advogado: ')[1:])
        retorno['reu'] = parte_reu.split('Advogado: ')[0]
        retorno['advogados_reu'] = ''.join(parte_reu.split('Advogado: ')[1:])
        retorno['comarca'] = dado[corte_jurisdicao:corte_inicial] 
        retorno['relator'] = dado[dado.find('Relator: '):corte_final]
        
        return retorno

        
    def extrair_decisao(self, dado):
        retorno = dict()
        corte_inicial = re.search(extract.pattern_processo, dado).span()[1]
        dado = dado[corte_inicial:]
        corte_final = re.search(extract.pattern_decisao, dado).span()[0]

        corte_jurisdicao = re.search(extract.pattern_jurisdicao, dado).span()[0]
        idx_inicio_autor = re.search(extract.pattern_autor, dado).span()[0]
        idx_inicio_reu = re.search(extract.pattern_reu, dado).span()[0]


        if idx_inicio_autor < idx_inicio_reu:
            corte_inicial = idx_inicio_autor
            inicial = 'autor'
        else:
            corte_inicial = idx_inicio_reu
            inicial = 'reu'

        cabecalho = dado[corte_inicial:corte_final]


        parte_autor = cabecalho[re.search(extract.pattern_autor, cabecalho).span()[0]:re.search(extract.pattern_reu, cabecalho).span()[0]]
        parte_reu = cabecalho[re.search(extract.pattern_reu, cabecalho).span()[0]:]
        retorno['processo'] = re.search(extract.pattern_processo, dado).group()
        retorno['autor'] = re.sub(extract.pattern_autor,'',parte_autor.split('Advogado: ')[0])
        retorno['advogados_autor'] = ''.join(parte_autor.split('Advogado: ')[1:])
        retorno['reu'] = parte_reu.split('Advogado: ')[0]
        retorno['advogados_reu'] = ''.join(parte_reu.split('Advogado: ')[1:])
        comarca = dado[corte_jurisdicao:corte_inicial]
        if comarca:
            retorno['comarca'] = comarca
        else:
            texto_cortado = dado[corte_jurisdicao:]
            corte_jurisdicao = re.search(extract.pattern_jurisdicao, texto_cortado).span()[0]
            if inicial == 'autor':
                corte_comarca = re.search(extract.pattern_autor, texto_cortado).span()[0]
            else:
                corte_comarca = re.search(extract.pattern_reu, texto_cortado).span()[0]
            retorno['comarca'] = texto_cortado[corte_jurisdicao:corte_comarca]
        retorno['relator'] = dado[dado.find('Relator: '):corte_final]
        return retorno


    def extrair_intimacao_1(self, dado):
        retorno = dict()
        dado = dado.replace('(s):','')
        corte_inicial = re.search(extract.pattern_processo, dado).span()[1]
        corte_final = re.search(extract.pattern_decisao, dado).span()[0]
        if corte_final < corte_inicial:
            dado = dado[corte_inicial:]
        else:
            dado = dado[corte_final:]
            corte_inicial = 1
            

        corte_final = re.search(extract.pattern_decisao, dado).span()[0]    
        corte_jurisdicao = re.search(extract.pattern_jurisdicao, dado).span()[0]
        idx_inicio_autor = re.search(extract.pattern_autor, dado).span()[0]
        idx_inicio_reu = re.search(extract.pattern_reu, dado).span()[0]


        if idx_inicio_autor < idx_inicio_reu:
            corte_inicial = idx_inicio_autor
            inicial = 'autor'
        else:
            corte_inicial = idx_inicio_reu
            inicial = 'reu'

        cabecalho = dado[corte_inicial:corte_final]


        parte_autor = cabecalho[re.search(extract.pattern_autor, cabecalho).span()[0]:re.search(extract.pattern_reu, cabecalho).span()[0]]
        parte_reu = cabecalho[re.search(extract.pattern_reu, cabecalho).span()[0]:]
        retorno['processo'] = re.search(extract.pattern_processo, dado).group()
        retorno['autor'] = self.remover_dados(parte_autor.split('Advogado')[0])
        retorno['advogados_autor'] = ''.join(parte_autor.split('Advogado')[1:])
        retorno['reu'] = self.remover_dados(parte_reu.split('Advogado')[0])
        retorno['advogados_reu'] = ''.join(parte_reu.split('Advogado')[1:])
        comarca = dado[corte_jurisdicao:corte_inicial]
        if comarca:
            retorno['comarca'] = comarca
        else:
            texto_cortado = dado[corte_jurisdicao:]
            corte_jurisdicao = re.search(extract.pattern_jurisdicao, texto_cortado).span()[0]
            if inicial == 'autor':
                corte_comarca = re.search(extract.pattern_autor, texto_cortado).span()[0]
            else:
                corte_comarca = re.search(extract.pattern_reu, texto_cortado).span()[0]
            retorno['comarca'] = texto_cortado[corte_jurisdicao:corte_comarca]
        retorno['relator'] = dado[dado.find('Relator: '):corte_final]
        return retorno


    def extrair_intimacao_2(self, dado):
        retorno = dict()
        dado = dado.replace('(s):','')
        corte_inicial = re.search(extract.pattern_processo, dado).span()[1]
        corte_final = re.search(extract.pattern_decisao, dado).span()[0]
        if corte_final > corte_inicial:
            dado = dado[corte_inicial:]
        else:
            dado = dado[corte_final:]
            corte_inicial = 1
            

        corte_final = re.search(extract.pattern_decisao, dado).span()[0]    
        corte_jurisdicao = re.search(extract.pattern_jurisdicao, dado).span()[0]
        idx_inicio_autor = re.search(extract.pattern_autor, dado).span()[0]
        idx_inicio_reu = re.search(extract.pattern_reu, dado).span()[0]


        if idx_inicio_autor < idx_inicio_reu:
            corte_inicial = idx_inicio_autor
            inicial = 'autor'
        else:
            corte_inicial = idx_inicio_reu
            inicial = 'reu'

        cabecalho = dado[corte_inicial:corte_final]


        parte_autor = cabecalho[re.search(extract.pattern_autor, cabecalho).span()[0]:re.search(extract.pattern_reu, cabecalho).span()[0]]
        parte_reu = cabecalho[re.search(extract.pattern_reu, cabecalho).span()[0]:]
        retorno['processo'] = re.search(extract.pattern_processo, dado).group()
        retorno['autor'] = self.remover_dados(parte_autor.split('Advogado')[0])
        retorno['advogados_autor'] = ''.join(parte_autor.split('Advogado')[1:])
        retorno['reu'] = self.remover_dados(parte_reu.split('Advogado')[0])
        retorno['advogados_reu'] = ''.join(parte_reu.split('Advogado')[1:])
        comarca = dado[corte_jurisdicao:corte_inicial]
        if comarca:
            retorno['comarca'] = comarca
        else:
            texto_cortado = dado[corte_jurisdicao:]
            corte_jurisdicao = re.search(extract.pattern_jurisdicao, texto_cortado).span()[0]
            if inicial == 'autor':
                corte_comarca = re.search(extract.pattern_autor, texto_cortado).span()[0]
            else:
                corte_comarca = re.search(extract.pattern_reu, texto_cortado).span()[0]
            retorno['comarca'] = texto_cortado[corte_jurisdicao:corte_comarca]
        retorno['relator'] = dado[dado.find('Relator: '):corte_final]
        return retorno
