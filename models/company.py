# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .. import defs

class Company(models.Model):
    _inherit = 'res.partner'

    prd_company_type = fields.Selection(defs.COMPANYTYPE.attrs.items(), string='公司类型')
    prd_charge_type = fields.Selection(defs.CHARGETYPE.attrs.items(), string='计费类型')
    prd_charge_count = fields.Integer('计数')
    prd_leader_id= fields.Many2one('res.partner', string='负责人') 

    @api.onchange('prd_leader_id')
    def _onchange_prd_leader_id(self):
            self.phone = self.prd_leader_id.phone
            self.email = self.prd_leader_id.email
            self.mobile = self.prd_leader_id.mobile



    



