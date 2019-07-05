# -*- coding: utf-8 -*-
import qrcode
from odoo import models, fields, api
from .. import defs
import sys,os 
import logging
_logger = logging.getLogger(__name__)
class Job(models.Model):
    _inherit = 'hr.job'

    name = fields.Char('职位名称',default ="New")
    post_id= fields.Many2one('company_prd.post','工作岗位')
    company_prd_id = fields.Many2one('company_prd.company', string='公司')


