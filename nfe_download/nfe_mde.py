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

from openerp import models, api, fields

class Nfe_Mde(models.Model):
    _name = 'nfe.mde'
    
    chNFe = fields.Integer(string="Chave de Acesso", size=44, readonly=True)
    nSeqEvento = fields.Integer(string="Número Sequencial", readonly=True)
    xNome = fields.Char(string="Razão Social", readonly=True)
    partner_id = fields.Many2one('res.partner',string='Partner')
    dEmi = fields.Datetime(string="Data Emissão", readonly=True)
    tpNF = fields.Integer(string="Tipo de Operação", readonly=True)
    vNF = fields.Integer(string="Valor Total da NF-e", readonly=True)
    cSitNFe = fields.Integer(string="Situação da NF-e", readonly=True)
    cSitConf = fields.Integer(string="Situação da Manifestação", readonly=True)
    formInclusao = fields.Char(string="Forma de Inclusão", readonly=True)
    dataInclusao = fields.Datetime(string="Data de Inclusão", readonly=True)
    versao = fields.Integer(string="Versão", readonly=True)

    @api.one
    def action_search_nfe(self):
        print "Acao ! action_search_nfe"
        return True

    @api.one
    def action_known_emission(self):
        print "Acao ! action_known_emission"
        return True

    @api.one
    def action_confirm_operation(self):
        print "Acao ! action_confirm_operation"
        return True
    
    @api.one
    def action_unknown_operation(self):
        print "Acao ! action_unknown_operation"
        return True

    @api.one    
    def action_not_operation(self):
        print "Acao ! action_not_operation"
        return True
    
    @api.one
    def action_download_xml(self):
        print "Acao ! action_download_xml"
        return True
