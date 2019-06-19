# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .. import defs
import logging
from .. import API
_logger = logging.getLogger(__name__)

class Post(models.Model):
    _name = "company_prd.post"

    name = fields.Char('职位')
    post_category = fields.Selection(defs.POSTTYPE.attrs.items(), string='职位分类')
    survey_id = fields.Many2one(
        'survey.survey', "测评表单",)
    prd_id = fields.Char('PRD-ID')

    def sync_from_prd(self):
        my_position = API.ApiPrd()
        sync_data = my_position.get_position()
        for position in sync_data:
            rs = self.search( [('prd_id', '=', position['postValue']) ] )
            if rs.exists():
                rs.write({
                            'name': position['postLabel'],
                            })
            else:
                self.create({
                            'prd_id': str(position['postValue']),
                            'name': position['postLabel'],
                            })
            _logger.info("################Position:%s######################" % position['postValue'])
            self.env['survey.survey'].sync_from_prd(position['postValue'])
