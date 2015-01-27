#coding=utf-8
###############################################################################
#                                                                             #
# Copyright (C) 2015  Danimar Ribeiro www.trustcode.com.br                    #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################
import re
import os
import base64
from pysped.nfe import ProcessadorNFe

def __processo(company):
    
    p = ProcessadorNFe()
    p.ambiente = int(company.nfe_environment)
    p.estado = company.partner_id.l10n_br_city_id.state_id.code
    p.certificado.stream_certificado = base64.decodestring(company.nfe_a1_file)
    p.certificado.senha = company.nfe_a1_password
    p.salvar_arquivos      = True
    p.contingencia_SCAN   = False
    p.caminho = company.nfe_export_folder
    return p


def _format_nse(nsu):
    nsu = long(nsu)
    return "%015d" % (nsu,)

def distribuicao_nfe(company, ultimo_nsu):
    ultimo_nsu = _format_nse(ultimo_nsu)
    p = __processo(company)
    cnpj_partner = re.sub('[^0-9]','', company.cnpj_cpf)   
    result = p.consultar_distribuicao(cnpj_cpf=cnpj_partner, ultimo_nsu=ultimo_nsu, nsu='')
    
    if result.resposta.status == 200: #Webservice ok
        if result.resposta.cStat.valor == '137' or result.resposta.cStat.valor == '138':
            
            return { 'code': result.resposta.cStat.valor, 'message': result.resposta.xMotivo.valor,
               'list_nfe': result.resposta.loteDistDFeInt.docZip}
        else:
            return { 'code': result.resposta.cStat.valor, 'message': result.resposta.xMotivo.valor,
               'file_sent': result.envio.xml, 'file_returned': result.resposta.xml }
    else:
        return { 'code': result.resposta.status, 'message': result.resposta.reason, 
                'file_sent': result.envio.xml, 'file_returned': None }
    
def download_nfe(company, list_nfe):
    p = __processo(company)
    cnpj_partner = re.sub('[^0-9]','', company.cnpj_cpf)   
    result = p.baixar_notas_destinadas(cnpj=cnpj_partner, lista_chaves=list_nfe)
    import_folder = company.nfe_import_folder
    
    if result.resposta.status == 200: #Webservice ok
        if result.resposta.cStat.valor == '139':
            list_nfe = []
            
            for nfe in result.resposta.retNFe:
                
                nome_arq = os.path.join(import_folder, 'download_nfe/')
                nome_arq = nome_arq + '-download-nfe.xml'
                arq = open(nome_arq, 'w')
                arq.write(nfe.procNFeZip.valor.encode('utf-8'))
                arq.close()
                
                item = { 'file_xml': nome_arq, 'code': nfe.cStat.valor, 'message': nfe.xMotivo.valor }
                list_nfe.append(item)       
            
            return list_nfe
        else:
            return { 'code': result.resposta.cStat.valor, 'message': result.resposta.xMotivo.valor,
                   'file_sent': result.envio.xml, 'file_returned': result.resposta.xml }
    else:
        return { 'code': result.resposta.status, 'message': result.resposta.reason, 
                'file_sent': result.envio.xml, 'file_returned': None }
 
    