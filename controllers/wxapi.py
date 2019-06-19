import logging
from odoo import http,exceptions
from odoo.http import request
from .base import BaseController,error_code
import json
from .. import defs

_logger = logging.getLogger(__name__)

class WxProject(http.Controller, BaseController):

    @http.route('/<string:sub_domain>/wxapi/job/add',auth='public', methods=['POST'], csrf=False)
    def job_add(self,sub_domain,token=None,**post):
        res, wechat_user, entry = self._check_user(sub_domain, token)
        if res:return res
        post = json.loads(post["data"])
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

        