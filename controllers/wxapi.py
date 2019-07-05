import logging
from odoo import http,exceptions,fields
from odoo.http import request
from .base import BaseController,error_code
import json
from .. import defs
import random
from PIL import Image
import sys,os 
from .tools import get_wx_session_info, get_wx_user_info, get_decrypt_info,get_wx_app_token

_logger = logging.getLogger(__name__)

class WxProject(http.Controller, BaseController):

    @http.route('/<string:sub_domain>/user/check-token', auth='public', methods=['GET'])
    def check_token(self, sub_domain, token=None, **kwargs): 
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret
            if not token:
                return self.res_err(300)
            access_token = request.env(user=1)['wxapp.access_token'].search([
                ('token', '=', token),
            ])
            if not access_token:
                return self.res_err(901)
            return self.res_ok()

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    @http.route('/<string:sub_domain>/user/wxapp/login', auth='public', methods=['GET', 'POST'],csrf=False)
    def login(self, sub_domain, code=None, **kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret
            config = request.env['wxapp.config'].sudo()
            if not code:
                return self.res_err(300)
            app_id = config.get_config('app_id', sub_domain)
            secret = config.get_config('secret', sub_domain)
            if not app_id or not secret:
                return self.res_err(404)

            session_info = get_wx_session_info(app_id, secret, code)
            if session_info.get('errcode'):
                return self.res_err(-1, session_info.get('errmsg'))

            open_id = session_info['openid']
            wechat_user = request.env(user=1)['wxapp.user'].search([
                ('open_id', '=', open_id),
            ])
            if not wechat_user:
                return self.res_err(10000)

            wechat_user2 = request.env(user=1)['wxapp.user'].search([
                ('open_id', '=', open_id),
                ('company_id.is_active', '=', True)
            ])
            if not wechat_user2:
                return self.res_err(11000)

            wechat_user.write({'last_login': fields.Datetime.now(), 'ip': request.httprequest.remote_addr})
            access_token = request.env(user=1)['wxapp.access_token'].search([
                ('open_id', '=', open_id),
                #('create_uid', '=', user.id)
            ])

            if not access_token:
                session_key = session_info['session_key']
                access_token = request.env(user=1)['wxapp.access_token'].create({
                    'open_id': open_id,
                    'session_key': session_key,
                    'sub_domain': sub_domain,
                })
            else:
                access_token.write({'session_key': session_info['session_key']})

            data = {
                'token': access_token.token,
                'uid': wechat_user.id,
                'info': self.get_user_info(wechat_user)
            }
            return self.res_ok(data)

        except AttributeError:
            return self.res_err(404)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    @http.route('/<string:sub_domain>/api/company/check', auth='public', methods=['POST'], csrf=False)
    def check_company(self,sub_domain,email):
        Account = request.env(user=1)['res.users'] 
        res = Account.search([('login','=',email)])
        
        if res :return self.res_err(-3)
        return self.res_ok()

    @http.route('/<string:sub_domain>/user/wxapp/register/complex', auth='public', methods=['GET', 'POST'], csrf=False)
    def register(self, sub_domain, code=None, encryptedData=None, iv=None, **kwargs):
        '''
        用户注册
        '''
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            config = request.env['wxapp.config'].sudo()

            encrypted_data = encryptedData
            if not code or not encrypted_data or not iv:
                return self.res_err(300)

            app_id = config.get_config('app_id', sub_domain)
            secret = config.get_config('secret', sub_domain)

            if not app_id or not secret:
                return self.res_err(404)

            session_key, user_info = get_wx_user_info(app_id, secret, code, encrypted_data, iv)
            
            wechat_user = request.env(user=1)['wxapp.user'].search([
                ('open_id', '=', user_info['openId']),
                #('create_uid', '=', user.id)
            ])
            if wechat_user:
                return self.res_err(11000)

            Company = request.env(user=1)['company_prd.company']
            Account = request.env(user=1)['res.users']

            my_company = Company.create({'name':kwargs['company_name'],'is_company':True,'active':False,'prd_company_type':int(kwargs['prd_company_type'])})
            my_account = Account.create({'login':kwargs['email'],'partner_id':my_company.partner_id.id,'company_id':1})

            vals = {
                'name': kwargs['contactor'],
                'nickname': user_info['nickName'],
                'open_id': user_info['openId'],
                'gender': user_info['gender'],
                'language': user_info['language'],
                'country': user_info['country'],
                'province': user_info['province'],
                'city': user_info['city'],
                'avatar_url': user_info['avatarUrl'],
                'register_ip': request.httprequest.remote_addr,
                'user_id': my_account.id,
                'partner_id': None,
                'company_id': my_company.id,
                'parent_id':my_company.partner_id.id,
                'email':kwargs['email'],
                'phone':kwargs['phone'],
            }
            my_wxappuser = request.env(user=1)['wxapp.user'].create(vals)
            my_company.write({'prd_leader_id': my_wxappuser.partner_id.id,'email':kwargs['email'],'phone':kwargs['phone']})
            my_account.write({'partner_id':my_wxappuser.partner_id.id})

            return self.res_ok()

        except AttributeError:
            return self.res_err(404)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    @http.route('/<string:sub_domain>/wxapi/job/add',auth='public', methods=['POST'], csrf=False)
    def job_add(self,sub_domain,token=None,**post):
        res, wechat_user, entry = self._check_user(sub_domain, token)
        if res:return res
        config = request.env['wxapp.config'].sudo()

        app_id = config.get_config('app_id', sub_domain)
        secret = config.get_config('secret', sub_domain)

        if not app_id or not secret:
            return self.res_err(404)
        access_token = get_wx_app_token(app_id,secret,'client_credential')

        post = json.loads(post["data"])
        try:
            Job = request.env(user=1)['hr.job']      
            my_job = Job.create({'name':post['post_name'],'post_id': post['post_id'],'no_of_recruitment':post['no_of_recruitment']})
            _data = {
                "dateAdd": my_job.create_date,
                "id": my_job.id
            }
            my_job.write({'survey_id':my_job.post_id.survey_id.id,'company_prd_id':wechat_user.company_id.id})
            #defs.create_qrcode(request.httprequest.base_url.split('/'+sub_domain)[0],my_job.id,wechat_user.backend_id.id)
            defs.getWXACodeUnlimit(access_token['access_token'],request.httprequest.base_url.split('/'+sub_domain)[0],my_job.id)

            return self.res_ok(_data)
        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e)

    @http.route('/<string:sub_domain>/wxapi/job/list', auth='public', methods=['GET'])
    def job_list(self, sub_domain, token=None):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res
            job_list = request.env['hr.job'].sudo().search([('create_uid','=',wechat_user.backend_id.id)])
            if not job_list:return self.res_err(404)
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
            return self.res_err(-1, e)


    @http.route('/wxapi/upload', auth='public',methods=['POST','GET'], csrf=False)
    def license_img(self,**post):
        _logger.info("###########%s#################gogoggo" % post)
    
        fn = str(random.randint(0, 100)) + '.png'
        avata = post['file']
        
        model_url = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/static/images/license/'
        _logger.info("#######打开文件%s" % model_url)
        new = Image.open(avata)
        pic_dir = os.path.join(model_url, fn)
        _logger.info("#######保存文件")
        new.save(pic_dir)
        _logger.info("#######成功保存文件")

    def get_user_info(self, wechat_user):
        data = {
            'base':{
                'mobile': wechat_user.phone,
                'userid': '',
            },
        }
        return data

    @http.route('/<string:sub_domain>/user/detail', auth='public', methods=['GET'])
    def detail(self, sub_domain, token=None):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            data = self.get_user_info(wechat_user)
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    @http.route('/<string:sub_domain>/user/wxapp/bindMobile', auth='public', methods=['GET', 'POST'], csrf=False)
    def bind_mobile(self, sub_domain, token=None, encryptedData=None, iv=None, **kwargs):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            config = request.env['wxapp.config'].sudo()

            encrypted_data = encryptedData
            if not token or not encrypted_data or not iv:
                return self.res_err(300)

            app_id = config.get_config('app_id', sub_domain)
            secret = config.get_config('secret', sub_domain)

            if not app_id or not secret:
                return self.res_err(404)

            access_token = request.env(user=1)['wxapp.access_token'].search([
                ('token', '=', token),
            ])
            if not access_token:
                return self.res_err(901)
            session_key = access_token[0].session_key

            _logger.info('>>> decrypt: %s %s %s %s', app_id, session_key, encrypted_data, iv)
            user_info = get_decrypt_info(app_id, session_key, encrypted_data, iv)
            _logger.info('>>> bind_mobile: %s', user_info)
            wechat_user.write({'phone': user_info.get('phoneNumber')})

            return self.res_ok()

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    @http.route('/<string:sub_domain>/wxapi/applicant/add',auth='public', methods=['POST'], csrf=False)
    def applicant_add(self,sub_domain,token=None,**kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret
            
            vals = {
                    'name': kwargs['name'],
                    'email_from':kwargs['email'],
                    'partner_mobile':kwargs['phone'],
                    'job_id':int(kwargs['job_id']),
                }
            my_applicant = request.env(user=1)['hr.applicant'].create(vals)

            res_data={
                'applicant_id':my_applicant.id,
                'survey_id':my_applicant.job_id.survey_id.id
            }
            return self.res_ok(res_data)
        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e)



    @http.route('/<string:sub_domain>/wxapi/survey/page',auth='public', methods=['get'])
    def survey_page(self,sub_domain,**kwargs):
        ret, entry = self._check_domain(sub_domain)
        if ret:return ret
        config = request.env['wxapp.config'].sudo()
        app_id = config.get_config('app_id', sub_domain)
        secret = config.get_config('secret', sub_domain)
        if not app_id or not secret:
                return self.res_err(404)
        try:
            survey_page = request.env['survey.page'].sudo().search([('survey_id','=',int(kwargs['surveyid']))])

            if not survey_page:
                return self.res_err(404)
            data = [
                {
                    "id":page.id,
                    "name": page.title,
                } for page in survey_page
            ]
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e)

    @http.route('/<string:sub_domain>/wxapi/survey/question',auth='public', methods=['get'])
    def survey_question(self,sub_domain,**kwargs):
        ret, entry = self._check_domain(sub_domain)
        if ret:return ret
        config = request.env['wxapp.config'].sudo()
        app_id = config.get_config('app_id', sub_domain)
        secret = config.get_config('secret', sub_domain)
        if not app_id or not secret:
            return self.res_err(404)
        try:
            survey_question = request.env['survey.question'].sudo().search([('page_id','=', int(kwargs['target']))])
            survey_label = request.env['survey.label']

            if not survey_question:
                return self.res_err(404)

            data = [
                {
                    "id":question.id,
                    "question": question.question,
                    "label":self.survey_label(question.id)
                } for question in survey_question
            ]
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e)

    def survey_label(self,question_id):
        try:
            survey_label = request.env['survey.label'].sudo().search([('question_id','=',question_id)])

            if not survey_label:
                return self.res_err(404)

            data = [
                {
                    "id":label.id,
                    "value": label.value,
                    "prd_uuid":label.prd_uuid
                } for label in survey_label
            ]
            return data

        except Exception as e:
            _logger.exception(e)

    @http.route('/<string:sub_domain>/wxapi/survey/user_input',auth='public', methods=['POST'], csrf=False)
    def user_input(self,sub_domain,token=None,**kwargs):
        _logger.info(kwargs)
        try:
            ret, entry = self._check_domain(sub_domain)
            user_input = request.env(user=1)['survey.user_input'].create({'survey_id': int(kwargs['survey_id']),'state':'skip'})
            kwargs.pop('survey_id')
            applicant = request.env(user=1)['hr.applicant'].browse([int(kwargs['applicant'])])
            if applicant:
                applicant.write({
                    'response_id': user_input.id,
                })
            kwargs.pop('applicant')
            
            for key,value in kwargs.items():
                vals ={
                    "user_input_id":user_input.id,
                    'survey_id': user_input.survey_id.id,
                    'question_id':int(key),
                    'value_suggested':int(value),
                    'answer_type':'suggestion'
                }
                user_input_line = request.env(user=1)['survey.user_input_line'].create(vals)

            return self.res_ok(user_input)
        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e)

    @http.route('/<string:sub_domain>/wxapi/job/info',auth='public', methods=['get'])
    def get_job_info(self,sub_domain,**kwargs):
        ret, entry = self._check_domain(sub_domain)
        if ret:return ret
        config = request.env['wxapp.config'].sudo()
        app_id = config.get_config('app_id', sub_domain)
        secret = config.get_config('secret', sub_domain)
        if not app_id or not secret:
            return self.res_err(404)
        try:
            job_info = request.env(user=1)['hr.job'].browse([int(kwargs['job_id'])])
            data ={
                "job_id":job_info.id,
                "job_name":job_info.name,
                "company":job_info.company_prd_id.name}
            if job_info:
                return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e)

    @http.route('/<string:sub_domain>/wxapi/applicant/list', auth='public', methods=['GET'])
    def applicant_list(self, sub_domain, token=None):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res
            applicant_list = request.env['hr.applicant'].sudo().search([])

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