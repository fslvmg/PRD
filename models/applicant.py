import uuid
from odoo import models, fields, api


class Applicant(models.Model):
    _inherit = 'hr.applicant'

    token = fields.Char('token', default=lambda self: str(uuid.uuid4()), readonly=True, required=True, copy=False)
    employee_id = fields.Many2one('hr.employee', string='员工信息') 
    ip =fields.Char('IP')
    wx_openid =fields.Char('wx_openid')
    is_pass = fields.Boolean(string='录用',default=False)
    is_synced = fields.Boolean(string='已同步',default=False)


            