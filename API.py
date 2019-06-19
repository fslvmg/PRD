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
        content_obj=json.loads(res.content)
        if content_obj:
            return content_obj[0]
    
    def post_data(self,data):
        path =PRD_URL+"/rest/companyInfo"
        headers = {'Content-Type': 'application/json'}
        r = requests.post(path,data,headers =headers)
        return r.text


        