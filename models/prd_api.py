import uuid
from odoo import models, fields, api
from .. import defs
import logging
from .. import API
_logger = logging.getLogger(__name__)

class PrdCompany(models.Model):
    _inherit = 'res.partner'

    prd_code = fields.Char('Prd-Code', default=lambda self: str(uuid.uuid4()), readonly=True, required=True, copy=False)
    prd_company_type = fields.Selection(defs.COMPANYTYPE.attrs.items(), string='公司类型')
    prd_charge_type = fields.Selection(defs.CHARGETYPE.attrs.items(), string='计费类型')
    prd_charge_count = fields.Integer('计数')
    prd_leader_id= fields.Many2one('res.partner', string='负责人') 

    @api.onchange('prd_leader_id')
    def _onchange_prd_leader_id(self):
            self.phone = self.prd_leader_id.phone
            self.email = self.prd_leader_id.email
            self.mobile = self.prd_leader_id.mobile
    
    def sync_to_prd(self):
        self.ensure_one()
        my_company = API.ApiPrd()
        sync_data = my_company.post_company(self)
        _logger.info("################%s######################" % sync_data)
        
        return


class PrdEmployee(models.Model):
    _inherit = 'hr.employee'

    prd_enterpriesOld =fields.Char("曾就职企业")
    prd_enterpries =fields.Char("现就职企业")
    prd_unitPosiOld =fields.Char("现就职岗位")

class PrdSurvey(models.Model):
    _inherit = 'survey.survey'

    prd_id = fields.Integer("测评系统ID", required=True)

    def sync_from_prd(self, post_id):
        my_survey = API.ApiPrd()
        sync_data = my_survey.get_survey_by_id(post_id)

        if not sync_data :
            return
        survey = rs = self.search( [('prd_id', '=', sync_data['id']) ] )
        if rs.exists():
            rs.write({
                'title': sync_data['name'],
            })
        else:
            survey = self.create({
                'prd_id': int(sync_data['id']),
                'title': sync_data['name'],
            })
        obj_post = self.env['company_prd.post'].search( [('prd_id', '=', int(post_id))])
        if obj_post.exists():
                obj_post.write({
                    'survey_id': survey.id,
                })

        obj_page = self.env['survey.page']
        obj_question = self.env['survey.question']
        obj_label = self.env['survey.label']

        for page in sync_data["subjectGroupList"]:
            mypage =  obj_page.search( [('prd_id', '=', page["id"]),('survey_id','=',survey.id) ] )
            if mypage.exists():
                obj_page.write({
                    'title': page["id"],
                })
            else:
                mypage = obj_page.create({
                    'prd_id': int(page["id"]),
                    'title':page["id"],
                    'survey_id':survey.id
                })
            
            for question in page["subjectInfoList"]:
                myquestion = obj_question.search( [('prd_id', '=', question["id"]),('page_id','=',mypage.id) ] )
                if myquestion.exists():
                    obj_question.write({
                        'question':question["content"],
                        'type':'simple_choice',
                        'prd_idx':question["idx"],
                    })
                else:
                    myquestion = obj_question.create({
                        'prd_id':question["id"],
                        'question':question["content"],
                        'page_id':mypage.id,
                        'type':'simple_choice',
                        'prd_idx':question["idx"],
                    })
                for label in question["anserList"]:
                    mylabel = obj_label.search( [('prd_uuid', '=', label["uuid"]),('question_id','=',myquestion.id) ] )
                    if mylabel.exists():
                        obj_label.write({
                            'value':label["answer"],
                            'prd_sort':label["sort"],
                    })
                    else:
                        mylabel = obj_label.create({
                            'prd_uuid':label["uuid"],
                            'value':label["answer"],
                            'question_id':myquestion.id,
                            'prd_sort':label["sort"],
                        })      
            

class PrdPage(models.Model):
    _inherit = 'survey.page'

    prd_id = fields.Integer("测评系统ID", required=True)

class PrdQuestion(models.Model):
    _inherit = 'survey.question'

    prd_id = fields.Integer("测评系统ID", required=True)
    prd_idx = fields.Integer("测评系统idx")

class PrdLabel(models.Model):
    _inherit = 'survey.label'

    prd_uuid = fields.Char("测评系统UUID")
    prd_sort = fields.Integer("排序")
