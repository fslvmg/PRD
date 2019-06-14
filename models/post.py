# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .. import defs

class Post(models.Model):
    _name = "prd.post"

    name = fields.Char('职位')
    post_category = fields.Selection(defs.POSTTYPE.attrs.items(), string='职位分类')
    survey_id = fields.Many2one(
        'survey.survey', "测评表单",)
