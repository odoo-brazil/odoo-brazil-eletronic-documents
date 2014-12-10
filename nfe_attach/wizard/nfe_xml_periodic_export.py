# -*- encoding: utf-8 -*-

from openerp.osv import orm, fields
import glob
import os
import commands
import base64
from datetime import date

class NfeXmlPeriodicExport(orm.TransientModel):

    _name = 'nfe.xml.periodic.export'
    _description = 'Export NFes'
    _columns = {
        'name': fields.char('Nome', size=255),
        'start_period_id': fields.many2one('account.period', u'Período Inicial'),
        'stop_period_id': fields.many2one('account.period', u'Período Final'),
        'zip_file': fields.binary('Zip Files', readonly=True),
        'state': fields.selection([('init', 'init'),
                                   ('done', 'done')],
                                    'state',
                                    readonly=True),
    }

    _defaults = {
        'state': 'init',
    }

    def done(self, cr, uid, ids, context=False):
        return True

    def export(self, cr, uid, ids, context=False):
        result = False
        a = self.pool.get('res.company')

        # Define a empresa correta se for multcompany
        company_id = a._company_default_get(cr, uid)
        obj_res_company = a.browse(cr, uid, company_id)

        caminho = str(obj_res_company.nfe_import_folder)
        export_dir = str(obj_res_company.nfe_export_folder)

        #completa o caminho com homologacao ou producao
        if obj_res_company.nfe_environment == '1':
            caminho = os.path.join(caminho, 'producao')
        elif obj_res_company.nfe_environment == '2':
            caminho = os.path.join(caminho, 'homologacao')

        # Diretorios de importacao, diretorios com formato do ano e mes
        dirs_date = os.listdir(caminho)

        for obj in self.browse(cr, uid, ids):
            data = False
            caminho_arquivos = ''
            
            date_start = obj.start_period_id.date_start
            date_stop = obj.stop_period_id.date_stop
            
            bkp_name = 'bkp_' + date_start[:7] + '_' + date_stop[:7] + '.zip'

            for diretorio in dirs_date:
                # TODO tratar pastas que não são geradas pelo sistema (que não estão no formato (ano-mes) aaaa-mm)
                if (int(diretorio[:4]) >= int(date_start[:4]) and int(diretorio[5:]) >= int(date_start[5:7])) and \
                   (int(diretorio[:4]) <= int(date_stop[:4]) and int(diretorio[5:]) <= int(date_stop[5:7])):

                    caminho_aux = os.path.join(caminho, diretorio)
                    dirs_nfes = os.listdir(caminho_aux)

                    for diretorio_final in dirs_nfes:

                        caminho_final = os.path.join(caminho_aux, diretorio_final) + '/'
                        comando_cce = 'ls ' + caminho_final + '*-??-cce.xml'
                        comando_can = 'ls ' + caminho_final + '*-??-can.xml'
                        comando_nfe = 'ls ' + caminho_final + '*-nfe.xml| grep -E "[0-9]{44}-nfe.xml"'
                        comando_inv = 'ls ' + caminho_final + '*-inu.xml| grep -E "[0-9]{41}-inu.xml"'

                        if os.system(comando_cce) == 0:
                            str_aux = commands.getoutput(comando_cce)
                            caminho_arquivos = caminho_arquivos + str_aux + ' '

                        if os.system(comando_can) == 0:
                            str_aux = commands.getoutput(comando_can)
                            caminho_arquivos = caminho_arquivos + str_aux + ' '

                        if os.system(comando_inv) == 0:
                            str_aux = commands.getoutput(comando_inv)
                            caminho_arquivos = caminho_arquivos + str_aux + ' '

                        str_aux = commands.getoutput(comando_nfe)
                        if os.system(comando_nfe) == 0:
                            str_aux = commands.getoutput(comando_nfe)
                            caminho_arquivos = caminho_arquivos + str_aux + ' '

                    # troca \n por espaços
                    caminho_arquivos = caminho_arquivos.replace('\n', ' ')
                    result = os.system("zip -r " + os.path.join(export_dir, bkp_name) + ' ' + caminho_arquivos)
                    # teste_comando= commands.getoutput("zip -r " + os.path.join(export_dir, bkp_name) + ' ' + caminho_arquivos)

                    data = self.read(cr, uid, ids, [], context=context)[0]

                    orderFile=open(os.path.join(export_dir, bkp_name), 'r')
                    itemFile = orderFile.read()

                    self.write(cr, uid, ids, {'state': 'done', 'zip_file': base64.b64encode(itemFile),
                                              'name': bkp_name}, context=context)

        if data:
            return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': data['id'],
            'target': 'new',
        }
        return False