# -*- coding: utf-8 -*-
from odoo import http

# class CompanyPrd(http.Controller):
#     @http.route('/company_prd/company_prd/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/company_prd/company_prd/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('company_prd.listing', {
#             'root': '/company_prd/company_prd',
#             'objects': http.request.env['company_prd.company_prd'].search([]),
#         })

#     @http.route('/company_prd/company_prd/objects/<model("company_prd.company_prd"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('company_prd.object', {
#             'object': obj
#         })