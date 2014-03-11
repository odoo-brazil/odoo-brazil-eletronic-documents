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


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    def action_invoice_send_nfe(self, cr, uid, ids, context=None):
        result = super(AccountInvoice, self).action_invoice_send_nfe(cr, uid, 
            ids, context)

        result = {}

        for inv in self.browse(cr, uid, ids):
            event_obj = self.pool.get('l10n_br_account.document_event')
            xml = inv.account_document_event_ids[0].file_sent

            danfe = xml[:-8]+'.pdf'
            obj_attachment = self.pool.get('ir.attachment')

            key = inv.nfe_access_key

            try: 
                file_danfe=open(danfe,'r')
                nfe_danfe = file_danfe.read()        

                attachment_id = obj_attachment.create(cr, uid, {
                    'name':'{0}.pdf'.format(inv.nfe_access_key),
                    'datas': base64.b64encode(nfe_danfe),
                    'datas_fname': '.pdf', 
                    'description': '' or _('No Description'),
                    'res_model': 'account.invoice',
                    'res_id': inv.id,
                    'type': 'binary'
                    }, context)
            except IOError:
                key = 'erro'
            else:
                file_danfe.close()

            try:
                file_xml=open(xml,'r')
                nfe_xml = file_xml.read()

                attachment_id = obj_attachment.create(cr, uid, {
                    'name':'{0}-nfe.xml'.format(key),
                    'datas': base64.b64encode(nfe_xml),
                    'datas_fname': '.xml', 
                    'description': '' or _('No Description'),
                    'res_model': 'account.invoice',
                    'res_id': inv.id
                    }, context=context)
            except IOError:
                raise osv.except_osv(_('Warning!'), _('Verifique por problemas na transmissão!')) 
            else:
                file_xml.close()
        return True