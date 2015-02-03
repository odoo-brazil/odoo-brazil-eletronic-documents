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
import logging
import base64
import gzip
import cStringIO 
from datetime import datetime
from .service.nfe_download import distribuicao_nfe, download_nfe
from openerp import models, api, fields
from openerp.addons.nfe.sped.nfe.validator.config_check import validate_nfe_configuration
from pysped.nfe.leiaute import RetDistDFeInt_100

_logger = logging.getLogger(__name__)

class nfe_schedule(models.TransientModel):
    _name = 'nfe.schedule'
        
    state = fields.Selection(string="Estado", selection=[('init', 'Não iniciado'), ('done', 'Finalizado')],
                             default='init')
    
    @api.model
    def schedule_download(self):        
        companies = self.env['res.company'].search([])
        for company in companies:
            try:
                validate_nfe_configuration(company)
                nfe_result = distribuicao_nfe(company, company.last_nsu_nfe)            
                
                env_events = self.env['l10n_br_account.document_event']
                
                if nfe_result['code'] == '137' or nfe_result['code'] == '138':
                    
                    nfes = download_nfe(company, nfe_result['list_nfe'])    
                            
                    for nfe in nfes:
                                    
                        event = {'type':'12', 'response':'Download efetuado', 'company_id': company.id ,
                                 'file_returned': nfe['file_xml'], 'status':nfe_result['code'] , 
                                 'message': nfe_result['message'], 'create_date':datetime.now(), 
                                 'write_date':datetime.now(), 'end_date':datetime.now(),
                                 'state': 'done', 'origin': 'Scheduler Download' }
                    
                        env_events.create(event)        
                else:
                    
                    event = {'type':'12', 'response':'Consulta distribuição com problemas', 'company_id': company.id ,
                        'file_returned': nfe_result['file_returned'], 'file_sent': nfe_result['file_sent'] , 
                        'message': nfe_result['message'], 'create_date':datetime.now(), 
                        'write_date':datetime.now(), 'end_date':datetime.now(),
                        'status':nfe_result['code'], 'state': 'done', 'origin': 'Scheduler Download' }
                    
                    env_events.create(event)                
            except Exception as ex:
                _logger.error(str(ex),exc_info=True)

    @api.one
    def execute_download(self):
        self.schedule_download()
        arq = open('/home/danimar/projetos/exportacao/homologacao/dfe-resumo/2015-01/resumo_nfe-000000000000001.xml', 'r')
        xml = arq.read()
        arq.close()
        ret = RetDistDFeInt_100()
        ret.set_xml(xml)
        xml = ret.loteDistDFeInt.docZip[0].base64Binary.valor
        
        orig_file_desc = gzip.GzipFile(mode='r', 
                          fileobj=cStringIO.StringIO(base64.b64decode(xml)))
        orig_file_cont = orig_file_desc.read()
        orig_file_desc.close()
        print orig_file_cont
