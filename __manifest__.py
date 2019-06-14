# -*- coding: utf-8 -*-
{
    'name': "company_prd",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_recruitment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/company_views.xml',
        'views/post_views.xml',
        'views/job_views.xml',
        'views/applicant_views.xml',
        
        'views/joblist_template.xml',
        'views/applicant_template.xml',
        'views/wxapp_config_views.xml',
        'views/wxapp_user_views.xml',
        'views/mainMenu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}