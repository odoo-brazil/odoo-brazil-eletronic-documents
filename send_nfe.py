'''
Created on 22/08/2013

@author: danimar
'''

import time
import base64
from datetime import datetime

from openerp import pooler
from openerp.osv import orm
from openerp.tools.translate import _

class SendNFe(object):
    
    def open_wizard_for_send(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        inv_obj = self.pool.get('account.invoice')
        active_ids = self._get_invoice_ids(cr, uid, data, context)
        export_inv_ids = []
        export_inv_numbers = []
        company_ids = []
        err_msg = ''

        if not active_ids:
            err_msg = u'Não existe nenhum documento fiscal para ser exportado!'

        for inv in inv_obj.browse(cr, uid, active_ids, context=context):
            if inv.state not in ('sefaz_export'):
                err_msg += u"O Documento Fiscal %s não esta definida para ser \
                exportação para a SEFAZ.\n" % inv.internal_number
            elif not inv.issuer == '0':
                err_msg += u"O Documento Fiscal %s é do tipo externa e não \
                pode ser exportada para a receita.\n" % inv.internal_number
            else:
                inv_obj.write(cr, uid, [inv.id], {'nfe_export_date': False,
                                                  'nfe_access_key': False,
                                                  'nfe_status': False,
                                                  'nfe_date': False})

                message = "O Documento Fiscal %s foi \
                    exportado." % inv.internal_number
                inv_obj.log(cr, uid, inv.id, message)
                export_inv_ids.append(inv.id)
                company_ids.append(inv.company_id.id)

            export_inv_numbers.append(inv.internal_number)

        if len(set(company_ids)) > 1:
            err_msg += u'Não é permitido exportar Documentos \
            Fiscais de mais de uma empresa, por favor selecione Documentos \
            Fiscais da mesma empresa.'

        if export_inv_ids:
            if len(export_inv_numbers) > 1:
                name = 'nfes%s-%s.%s' % (
                    time.strftime('%d-%m-%Y'),
                    self.pool.get('ir.sequence').get(cr, uid, 'nfe.export'),
                    data['file_type'])
            else:
                name = 'nfe%s.%s' % (export_inv_numbers[0], data['file_type'])

            mod_serializer = __import__(
                'l10n_br_account.sped.nfe.serializer.' + data['file_type'],
                 globals(), locals(), data['file_type'])

            func = getattr(mod_serializer, 'nfe_export')
            nfes = func(
                cr, uid, export_inv_ids, data['nfe_environment'],
                '200', context)

            nfe_result_pool = self.pool.get('l10n_br_account.nfe_export_invoice_result')
            final_xml = ''
            for nfe in nfes:                
                xml_sent = ''
                if nfe["xml_type"] == "Danfe/NF-e":
                    xml_sent = nfe['xml_sent']
                else:
                    xml_sent = nfe['xml_sent'].encode('utf8')
                xml_result = nfe['xml_result'].encode('utf8')
                
                nfe_result_pool.create(
                    cr, uid, {'name': nfe['name'],
                        'name_result': nfe['name_result'],
                        'message': nfe['message'],
                        'xml_type': nfe['xml_type'],
                        'status': nfe['status'],
                        'wizard_id': data['id'],
                        'file': base64.b64encode(xml_sent),
                        'file_result': base64.b64encode(xml_result), })  
                if nfe["xml_type"] == "Danfe/NF-e":
                    final_xml = base64.b64encode(xml_result)              

            if final_xml != "":
                self.write(
                    cr, uid, ids, {'file': base64.b64encode(xml_result),
                    'state': 'done', 'name': name}, context=context)
            else:
                self.write(
                    cr, uid, ids, {'state': 'done'}, context=context)
            

        if err_msg:
            raise orm.except_orm(_('Error!'), _("'%s'") % _(err_msg, ))

        mod_obj = self.pool.get('ir.model.data')
        model_data_ids = mod_obj.search(
            cr, uid, [('model', '=', 'ir.ui.view'),
            ('name', '=', 'l10n_br_account_nfe_export_invoice_form')],
            context=context)
        resource_id = mod_obj.read(
            cr, uid, model_data_ids,
            fields=['res_id'], context=context)[0]['res_id']

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': data['id'],
            'views': [(resource_id, 'form')],
            'target': 'new',
        }
    
    def send(self, cr, uid, ids, nfe_environment, context=None):
        try:            
            from pysped.nfe import ProcessadorNFe
            from pysped.nfe import webservices_flags
        except ImportError as e:
            raise orm.except_orm(
                _(u'Erro!'), _(u"Biblioteca PySPED não instalada! " + str(e)))
                             
        pool = pooler.get_pool(cr.dbname)
        invoice = pool.get('account.invoice').browse(cr, uid, ids[0], context)
        
        company_pool = pool.get('res.company')        
        company = company_pool.browse(cr, uid, invoice.company_id.id)
                
        p = ProcessadorNFe()
        p.versao = '2.00' if (company.nfe_version == '200') else '1.10'
        p.estado = company.partner_id.l10n_br_city_id.state_id.code
        
        file_content_decoded = base64.decodestring(company.nfe_a1_file)
        filename = company.nfe_export_folder + 'certificate.pfx'
        fichier = open(filename,'w+')
        fichier.write(file_content_decoded)
        fichier.close()
                   
        p.certificado.arquivo = filename
        p.certificado.senha = company.nfe_a1_password
    
        p.salva_arquivos      = True
        p.contingencia_SCAN   = False
        p.caminho = company.nfe_export_folder
        
        nfe = self._serializer(cr, uid, ids, nfe_environment, context)
        result = []
        
        for processo in p.processar_notas(nfe):   
            #result.append({'status':'success', 'message':'Recebido com sucesso.', 'key': nfe[0].infNFe.Id.valor, 'nfe': processo.envio.xml})
            #result.append({'status':'success', 'message':'Recebido com sucesso.','key': nfe[0].infNFe.Id.valor, 'nfe': processo.resposta.xml})
                                                        
            status = processo.resposta.cStat.valor
            message = processo.resposta.xMotivo.valor
            name = 'xml_enviado.xml'
            name_result = 'xml_retorno.xml'
            file_sent = processo.envio.xml
            file_result = processo.resposta.xml
            
            type_xml = ''
            if processo.webservice == webservices_flags.WS_NFE_CONSULTA:
                type_xml = 'Situação NF-e'
            elif processo.webservice == webservices_flags.WS_NFE_SITUACAO:                
                type_xml = 'Status'
            elif processo.webservice == webservices_flags.WS_NFE_ENVIO_LOTE:
                type_xml = 'Envio NF-e'
            elif processo.webservice == webservices_flags.WS_NFE_CONSULTA_RECIBO:
                type_xml = 'Recibo NF-e'                        
                
            if processo.resposta.status == 200:
                
                resultado = {'name':name,'name_result':name_result, 'message':message, 'xml_type':type_xml, 
                    'status_code':status,'xml_sent': file_sent,'xml_result': file_result, 'status':'success'}
                            
                if processo.webservice == webservices_flags.WS_NFE_CONSULTA_RECIBO:                
                    for prot in processo.resposta.protNFe:
                        resultado["status_code"] = prot.infProt.cStat.valor
                        resultado["message"] = prot.infProt.xMotivo.valor
                        if prot.infProt.cStat.valor in ('100', '150', '110', '301', '302'):
                            nfe_xml = processo.resposta.dic_procNFe[prot.infProt.chNFe.valor].xml
                            danfe_pdf = processo.resposta.dic_procNFe[prot.infProt.chNFe.valor].danfe_pdf
                        
                            danfe_nfe = {'name':'danfe.pdf','name_result':'nfe_protocolada.xml', 
                                'message':prot.infProt.xMotivo.valor, 'xml_type':'Danfe/NF-e', 
                                'status_code':prot.infProt.cStat.valor,'xml_sent': danfe_pdf,
                                'xml_result': nfe_xml , 'status':'success'}
                            
                            result.append(danfe_nfe)
                            
                        else:
                            resultado["status"] = "error"
            else:
                resultado = {'name':name,'name_result':name_result, 'message':processo.resposta.original, 'xml_type':type_xml, 
                    'status_code':processo.resposta.status,'xml_sent': file_sent,'xml_result': file_result, 'status':'error'}
                
            result.append(resultado)
            
        return result
    