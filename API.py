from __future__ import unicode_literals
from odoo import fields
import requests
import json

PRD_URL ="http://39.108.182.91:8080/PRD"

class ApiPrd(object):

    def post_company(self,obj_company):
        company_data={
            "name":obj_company.name,
            "code":obj_company.prd_code,
            "type":obj_company.prd_company_type,
            "payModel":obj_company.prd_charge_type,
            "count":obj_company.prd_charge_count,
            "leader":obj_company.prd_leader_id.name,
            "phone":obj_company.phone,
            "email":obj_company.email,
            "posts":""
        }
        json_body = json.dumps(company_data,ensure_ascii=False)
        return json_body 

    def get_position(self):
        path =PRD_URL+"/rest/post"
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        res = requests.get(path,headers = headers) 
        obj_position=json.loads(res.content.decode('utf-8'))
        return obj_position
    
    def get_survey_by_id(self, post_id):

        path =PRD_URL+"/rest/%s" % post_id
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        res = requests.get(path,headers = headers) 
        content_obj=json.loads(res.content.decode('utf-8'))
        if content_obj:
            return content_obj[0]
    
    def post_data(self,data):
        path =PRD_URL+"/rest/companyInfo"
        headers = {'Content-Type': 'application/json'}
        r = requests.post(path,data,headers =headers)
        return r.text

    def post_applicant(self,obj_applicant):
        applicant_data={
            "company":obj_applicant.job_id.company_prd_id.name,
            "companyCode":obj_applicant.job_id.company_prd_id.prd_code,
            "name":obj_applicant.name,
            "code":obj_applicant.token,

            "ip":obj_applicant.ip,
            "phone":obj_applicant.partner_mobile,
            "source":"MyApplicant.source_id",

            "evaluationTime":obj_applicant.create_date.strftime("%Y-%m-%d %H:%M:%S"),
            "submitTime":obj_applicant.write_date.strftime("%Y-%m-%d %H:%M:%S"),
            "userTime":(obj_applicant.create_date-obj_applicant.write_date).seconds,
            "evaluationPost":obj_applicant.job_id.post_id.name,


            "sex":obj_applicant.emp_id.gender,
            "birthday":obj_applicant.emp_id.birthday,
            "edu":obj_applicant.emp_id.certificate,
            "enterpriesOld":obj_applicant.emp_id.prd_enterpriesOld,
            "enterpries":obj_applicant.emp_id.prd_enterpries,
            "unitPosiOld":obj_applicant.emp_id.prd_unitPosiOld,
            "residentialAddress":obj_applicant.emp_id.address_home_id.name,
            "address":obj_applicant.emp_id.place_of_birth
        }
        json_body = json.dumps(applicant_data,ensure_ascii=False)
        return json_body 

    def post_survey_by_applicant(self,obj_applicant,answer):
        survey_data={
            "companyName":obj_applicant.job_id.company_prd_id.name,
            "companyCode":obj_applicant.job_id.company_prd_id.prd_code,
            "userName":obj_applicant.name,
            "userCode":obj_applicant.token,
            "paperId":2,
            "evalDate":obj_applicant.response_id.create_date.strftime("%Y-%m-%d %H:%M:%S"),
            "useTime":(obj_applicant.response_id.create_date-obj_applicant.response_id.write_date).seconds,
            "ip":obj_applicant.ip or "",
            "address":obj_applicant.emp_id.place_of_birth or "",
            "source":"1",
            "sourceDetail":"MyApplicant.source_id",
            "evalPost":2,
            "answers":answer
        }
        print("==========================================================")
        json_body = json.dumps(survey_data,ensure_ascii=False)
        return json_body 

    def get_survey_user_input(self,obj_user_input_lines):
        input_data = [line.value_suggested.prd_uuid for line in obj_user_input_lines]
        return input_data
  

    