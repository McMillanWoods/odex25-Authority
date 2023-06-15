# -*- coding: utf-8 -*-
{
    'name': "Online Tendering",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase_requisition_custom','purchase_requisition','website','auth_signup','contacts'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/rules.xml',
        'security/ir.model.access.csv',
        'views/purchase_requsition_veiw.xml',
        'views/templates.xml',
        'views/tender_application.xml',
        'views/online_tender_configuration.xml',
        'sequence/seq.xml',
        'data/mail_templates.xml',
        'wizard/online_tendering_wizard.xml',
        'reports/online_tender_report.xml',
        'reports/report_actions.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb':[
        'static/src/xml/tender_templates.xml',
    ]
}