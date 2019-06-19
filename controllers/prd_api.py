from __future__ import unicode_literals
import logging
import datetime

from odoo import http,exceptions
from odoo.http import request
from .base import BaseController
from .. import defs
from .. import API
_logger = logging.getLogger(__name__)
PRD_URL ="http://39.108.182.91:8080/PRD"

class PrdAPI(http.Controller, BaseController):
        
    @http.route('/PRD/get/survey/<int:post_id>', auth='public', methods=['GET'])
    def get_survey(self, post_id,**kwargs):

        path =PRD_URL+"/rest/%s" % post_id
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        res = defs.requests.get(path,headers = headers) 
        content_obj=defs.json.loads(res.content)

        res_survey = content_obj[0]

        MySurvey = request.env(user=1)['survey.survey']
        MyPage =request.env(user=1)['survey.page']
        MyQuestion =request.env(user=1)['survey.question']
        MyLabel =request.env(user=1)['survey.label']

        survey_data={
            'prd_id':res_survey["id"],
            'title':res_survey["name"]
        }
        my_survey = MySurvey.create(survey_data)
        _logger.info("=============创建调查表单")

        for page in res_survey["subjectGroupList"]:
            page_data={
                'prd_id':page["id"],
                'title':page["id"],
                'survey_id':my_survey.id
            }
            my_page=MyPage.create(page_data)
            _logger.info("=============创建表单分组")
            for question in page["subjectInfoList"]:
                question_data={
                    'prd_id':question["id"],
                    'question':question["content"],
                    'page_id':my_page.id,
                    'type':'simple_choice',
                    'prd_idx':question["idx"],
                }
                my_question=MyQuestion.create(question_data)
                _logger.info("=============创建问题")
                for label in question["anserList"]:
                    label_data ={
                        'prd_uuid':label["uuid"],
                        'value':label["answer"],
                        'question_id':my_question.id,
                        'prd_sort':label["sort"],
                    }
                    my_label=MyLabel.create(label_data)
                    _logger.info("=============创建答案")

        _data = {
                "dateAdd": my_survey.create_date,
                "id": my_survey.id
            }
        return self.res_ok(_data)
    
    @http.route('/PRD/post/company', auth='public', methods=['GET'])
    def post_company(self,**kwargs):
        MyCompany = request.env(user=1)['res.partner'].search([
                ('is_company', '=', True),
                ('id', '=', 7)
            ])
        company_data={
            "name":MyCompany.name,
            "code":MyCompany.prd_code,
            "type":MyCompany.prd_company_type,
            "payModel":MyCompany.prd_charge_type,
            "count":MyCompany.prd_charge_count,
            "leader":MyCompany.prd_leader_id.name,
            "phone":MyCompany.phone,
            "email":MyCompany.email,
            "posts":""
        }
        json_body = defs.json.dumps(company_data)
        return json_body
    
    @http.route('/PRD/post/applicant', auth='public', methods=['GET'])
    def post_applicant(self,**kwargs):
        MyApplicant = request.env(user=1)['hr.applicant'].search([
                ('id', '=', 1)
            ])
        applicant_data={
            "company":MyApplicant.job_id.address_id.name,
            "companyCode":MyApplicant.job_id.address_id.prd_code,
            "name":MyApplicant.name,
            "code":MyApplicant.token,

            "ip":MyApplicant.ip,
            "phone":MyApplicant.partner_id.phone,
            "source":"MyApplicant.source_id",

            "evaluationTime":MyApplicant.create_date.strftime("%Y-%m-%d %H:%M:%S"),
            "submitTime":MyApplicant.write_date.strftime("%Y-%m-%d %H:%M:%S"),
            "userTime":(MyApplicant.create_date-MyApplicant.write_date).seconds,
            "evaluationPost":MyApplicant.job_id.post_id.name,


            "sex":MyApplicant.emp_id.gender,
            "birthday":MyApplicant.emp_id.birthday,
            "edu":MyApplicant.emp_id.certificate,
            "enterpriesOld":MyApplicant.emp_id.prd_enterpriesOld,
            "enterpries":MyApplicant.emp_id.prd_enterpries,
            "unitPosiOld":MyApplicant.emp_id.prd_unitPosiOld,
            "residentialAddress":MyApplicant.emp_id.address_home_id.name,
            "address":MyApplicant.emp_id.place_of_birth
        }
        json_body = defs.json.dumps(applicant_data,ensure_ascii=False)
        return json_body

    @http.route('/PRD/api/test', auth='public', methods=['GET'])
    def prd_test(self,**kwargs):
        mycompany = API.ApiPrdCompany()
        return mycompany.get_survey_by_id(3)
    

        
