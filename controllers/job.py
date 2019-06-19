# -*- coding: utf-8 -*-
import logging
from odoo import http,exceptions
from odoo.http import request
from .base import BaseController,error_code
from .. import defs
import json


_logger = logging.getLogger(__name__)

class PrdJob(http.Controller, BaseController):
        
    @http.route('/api/post/list', auth='public', methods=['GET'])
    def post_list(self, **kwargs):
        try:
            post_list = request.env['company_prd.post'].sudo().search([])

            if not post_list:
                return self.res_err(404)
            data = [
                {
                    "id":post.id,
                    "name": post.name,
                } for post in post_list
            ]
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)

    @http.route('/<string:sub_domain>/api/job/list', auth='public', methods=['GET'])
    def job_list(self, sub_domain, token=None):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res
            job_list = request.env['hr.job'].sudo().search([('create_uid','=',wechat_user.backend_id.id)])
            

            if not job_list:
                return self.res_err(404)
            data = [
                {
                    "id":each_job.id,
                    "name": each_job.name,
                    "no_of_recruitment":each_job.no_of_recruitment,
                    "application_count":each_job.application_count,
                } for each_job in job_list
            ]
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)

    @http.route('/<string:sub_domain>/api/job/add2',auth='public', methods=['POST'], csrf=False)
    def job_add(self,sub_domain,token=None,**post):
        _logger.info(post['data'])
        return
        res, wechat_user, entry = self._check_user(sub_domain, token)
        if res:return res
        #post = json.loads(post["data"])
        _logger.info(post)
        try:
            Job = request.env(user=wechat_user.backend_id.id)['hr.job']      
            my_job = Job.create({'name':post['post_name'],'post_id': post['post_id'],'no_of_recruitment':post['no_of_recruitment']})
            _data = {
                "dateAdd": my_job.create_date,
                "id": my_job.id
            }
            defs.create_qrcode(request.httprequest.base_url.split('/'+sub_domain)[0],my_job.id,wechat_user.backend_id.id)
            return self.res_ok(_data)
        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e)

    @http.route('/<string:sub_domain>/api/applicant/list', auth='public', methods=['GET'])
    def applicant_list(self, sub_domain, token=None):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res
            applicant_list = request.env(user=wechat_user.backend_id.id)['hr.applicant'].sudo().search([('create_uid','=',wechat_user.backend_id.id)])

            if not applicant_list:
                return self.res_err(404)
            data = [
                {
                    "id":applicant.id,
                    "name": applicant.partner_name,
                    "job":applicant.job_id.name,
                    "phone":applicant.partner_mobile,
                    "has_report":applicant.response_id.token,
                    "report_url":"/survey/print/%s/%s" % (applicant.job_id.id,applicant.response_id.token)
                } for applicant in applicant_list
            ]
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)

    @http.route('/api/job/add2',auth='user', type='http', website=True)
    def job_add2(self,**post):
        if not post:
            Post = request.env['prd.post']
            my_post = Post.search([])
            data ={'posts':my_post}
            return request.render('company_prd.job_add',data)
        
        Job = request.env['hr.job']
        my_job = Job.create({'name': post['job_name'],'no_of_recruitment':post['no_of_recruitment'],'description':post['description']})
        return request.redirect('/api/job/list')

    @http.route(['/applicant/start/<string:create_uid>/<int:job_id>',
                 '/applicant/start/<string:create_uid>/<int:job_id>/<string:token>'],
                type='http', auth='public',website=True)
    def start_applicant(self, create_uid,job_id, token=None, **post):
        survey_token = 'phantom'
        MyApplicant = request.env(user=create_uid)['hr.applicant']
        job = request.env(user=create_uid)['hr.job'].browse(int(job_id))
        # Test mode
        if not token or token == "phantom":
            _logger.info("[applicant] Phantom mode")   
            my_applicant = MyApplicant.create({'job_id':int(job_id) })
        else:
            my_applicant = MyApplicant.search([('token', '=', token)], limit=1)
            if my_applicant.response_id.token:
                survey_token = my_applicant.response_id.token
        data = {'job': job, 'survery_token':survey_token}
        return request.render('company_prd.applicant_init', data)

    @http.route('/<string:sub_domain>/api/company/register',auth='public', methods=['POST'], csrf=False)
    def company_register(self,sub_domain,token=None,**post):
        _logger.info("##########%s############33" % post)
        _logger.info("######################44")
        _logger.info("######################55")
        try:
            Company = request.env(user=1)['res.partner']     
            Account = request.env(user=1)['res.users']  
            my_company = Company.create({'name':post['company_name'],'is_company':True})
            my_contact = Company.create({'name':post['contactor'],'email':post['email'],'phone':post['phone'],'parent_id':my_company.id})
            my_company.write({'prd_leader_id': my_contact.id,'email':my_contact.email,'phone':my_contact.phone})
            my_account = Account.create({'login':my_contact.email,'partner_id':my_company.id,'company_id':1})
            _data = {
                "id": my_account.id
            }
            return self.res_ok(_data)
        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, "ww")
    
    @http.route('/<string:sub_domain>/api/company/check', auth='public', methods=['POST'], csrf=False)
    def check_company(self,sub_domain,email):
        _logger.info("######################%s55" % email)
        Account = request.env(user=1)['res.users'] 
        res = Account.search([('login','=',email)])
        
        if res :return self.res_err(-3)
        return self.res_ok()
        

