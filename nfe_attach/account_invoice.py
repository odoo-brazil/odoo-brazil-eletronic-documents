# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2014  KMEE - www.kmee.com.br - Luis Felipe Miléo              #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU General Public License for more details.                                 #
#                                                                             #
#You should have received a copy of the GNU General Public License            #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

import os
import base64
from openerp.osv import osv,orm, fields
from openerp.tools.translate import _
from openerp.addons.nfe.sped.nfe.processing.xml import monta_caminho_nfe

class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    # def action_invoice_send_nfe(self, cr, uid, ids, context=None):
    #     result = super(AccountInvoice, self).action_invoice_send_nfe(cr,
    #                                                     uid, ids, context)
    #
    #     result = {}
    #
    #     for inv in self.browse(cr, uid, ids):
    #         event_obj = self.pool.get('l10n_br_account.document_event')
    #         xml = inv.account_document_event_ids[0].file_sent
    #
    #         danfe = xml[:-8]+'.pdf'
    #         obj_attachment = self.pool.get('ir.attachment')
    #
    #         key = inv.nfe_access_key
    #
    #         try:
    #             file_danfe=open(danfe,'r')
    #             nfe_danfe = file_danfe.read()
    #
    #             attachment_id = obj_attachment.create(cr, uid, {
    #                 'name':'{0}.pdf'.format(inv.nfe_access_key),
    #                 'datas': base64.b64encode(nfe_danfe),
    #                 'datas_fname': '.pdf',
    #                 'description': '' or _('No Description'),
    #                 'res_model': 'account.invoice',
    #                 'res_id': inv.id,
    #                 'type': 'binary'
    #                 }, context)
    #         except IOError:
    #             key = 'erro'
    #         else:
    #             file_danfe.close()
    #
    #         try:
    #             file_xml=open(xml,'r')
    #             nfe_xml = file_xml.read()
    #
    #             attachment_id = obj_attachment.create(cr, uid, {
    #                 'name':'{0}-nfe.xml'.format(key),
    #                 'datas': base64.b64encode(nfe_xml),
    #                 'datas_fname': '.xml',
    #                 'description': '' or _('No Description'),
    #                 'res_model': 'account.invoice',
    #                 'res_id': inv.id
    #                 }, context=context)
    #         except IOError:
    #             raise osv.except_osv(_('Warning!'), _('Verifique por problemas na transmissão!'))
    #         else:
    #             file_xml.close()
    #     return True

    # def cancel_invoice_online(self, cr, uid, ids, justificative, context=None):
    #     result = super(AccountInvoice, self).cancel_invoice_online(cr,
    #                                 uid, ids, justificative, context)
    #
    #     result = {}
    #
    #     for inv in self.browse(cr, uid, ids):
    #         company_pool = self.pool.get('res.company')
    #         company = company_pool.browse(cr, uid, inv.company_id.id)
    #         nfe_key = inv.nfe_access_key
    #
    #         save_dir = os.path.join(monta_caminho_nfe(company, chave_nfe=nfe_key) + nfe_key + '-01-can.xml')
    #
    #         obj_attachment = self.pool.get('ir.attachment')
    #
    #         try:
    #             file_xml=open(save_dir,'r')
    #             nfe_xml = file_xml.read()
    #
    #             attachment_id = obj_attachment.create(cr, uid, {
    #                 'name':'{0}-01-can.xml'.format(nfe_key),
    #                 'datas': base64.b64encode(nfe_xml),
    #                 'datas_fname': '.xml',
    #                 'description': '' or _('No Description'),
    #                 'res_model': 'account.invoice',
    #                 'res_id': inv.id
    #                 }, context=context)
    #         except IOError:
    #             key = 'erro'
    #         else:
    #             file_xml.close()
    #
    #     return True

    # def cce_invoice_online(self, cr, uid, ids, sequencia, correcao, context=None):
    #
    #     for inv in self.browse(cr, uid, ids):
    #         company_pool = self.pool.get('res.company')
    #         company = company_pool.browse(cr, uid, inv.company_id.id)
    #         nfe_key = inv.nfe_access_key
    #         srt_aux = nfe_key + '-%02d-cce.xml' % sequencia
    #
    #         save_dir = os.path.join(monta_caminho_nfe(company, chave_nfe=nfe_key) + nfe_key + '-%02d-cce.xml' % sequencia)
    #
    #         obj_attachment = self.pool.get('ir.attachment')
    #
    #         try:
    #             file_xml=open(save_dir,'r')
    #             nfe_xml = file_xml.read()
    #
    #             attachment_id = obj_attachment.create(cr, uid, {
    #                 'name': srt_aux.format(nfe_key),
    #                 'datas': base64.b64encode(nfe_xml),
    #                 'datas_fname': '.xml',
    #                 'description': '' or _('No Description'),
    #                 'res_model': 'account.invoice',
    #                 'res_id': inv.id
    #                 }, context=context)
    #         except IOError:
    #             key = 'erro'
    #         else:
    #             file_xml.close()
    #
    #     return True


    def attach_file_event(self, cr, uid, ids, seq, att_type, ext, context):

        if seq == None:
            seq = 1

        for inv in self.browse(cr, uid, ids):
            company_pool = self.pool.get('res.company')
            company = company_pool.browse(cr, uid, inv.company_id.id)
            nfe_key = inv.nfe_access_key

            if att_type != 'nfe' and att_type != None:
                str_aux = nfe_key + '-%02d-%s.%s' % (seq, att_type, ext)
                save_dir = os.path.join(monta_caminho_nfe(company, chave_nfe=nfe_key) + str_aux)

            elif att_type == None and ext == 'pdf':
                str_aux = nfe_key + '.%s' % (ext)
                save_dir = os.path.join(monta_caminho_nfe(company, chave_nfe=nfe_key) + str_aux)

            elif att_type == 'nfe' and ext == 'xml':
                str_aux = nfe_key + '-%s.%s' % (att_type, ext)
                save_dir = os.path.join(monta_caminho_nfe(company, chave_nfe=nfe_key) + str_aux)

            obj_attachment = self.pool.get('ir.attachment')

            try:
                file_attc=open(save_dir,'r')
                attc = file_attc.read()

                attachment_id = obj_attachment.create(cr, uid, {
                    'name': str_aux.format(nfe_key),
                    'datas': base64.b64encode(attc),
                    'datas_fname': '.' + ext,
                    'description': '' or _('No Description'),
                    'res_model': 'account.invoice',
                    'res_id': inv.id
                    }, context=context)
            except IOError:
                key = 'erro'
            else:
                file_attc.close()

        return True


    def action_invoice_sent(self, cr, uid, ids, context=None):
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        attach_obj = self.pool.get('ir.attachment')
        attachment_ids = attach_obj.search(cr, uid, [('res_model', '=', 'account.invoice'), ('res_id', '=', ids[0])], context=context)
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'nfe_attach', 'email_template_nfe')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'account.invoice',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_invoice_as_sent': True,
            'attachment_ids': [(6, 0, attachment_ids)] ,
            })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    
class email_template(osv.Model):
    _inherit = 'email.template'
 
    def generate_email(self, cr, uid, template_id, res_id, context=None):
        context = context or {}
        values =  super(email_template, self).generate_email( cr, uid, template_id, res_id, context)
        if context.get('default_model') == 'account.invoice':
            values['attachment_ids'] = context.get('attachment_ids')
        return values
        
        
class res_company(osv.Model):
    _inherit = 'res.company'

    _columns = {
    'nfe_email': fields.text('Observação em Email NFe'),
            }
