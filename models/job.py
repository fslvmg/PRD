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
    post_id= fields.Many2one('prd.post','工作岗位')
    qrcode_url = fields.Char('二维码地址',compute='_get_qrcode_data')

    @api.onchange('post_id')
    def onchange_name(self):
        self.name = self.post_id.name
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data("http://192.168.31.138/applicant/start/"+str(self.id)+"/phantom")
        qr.make(fit=True)
        img = qr.make_image()
        # 保存到的地址
        model_url = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        img.save(model_url+'/static/images/qrcode-'+str(self.id)+'.png')


