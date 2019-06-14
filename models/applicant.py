import uuid
from odoo import models, fields, api


class Applicant(models.Model):
    _inherit = 'hr.applicant'

    name = fields.Char("Subject / Application Name", required=True,default='wwww')
    token = fields.Char('token', default=lambda self: str(uuid.uuid4()), readonly=True, required=True, copy=False)