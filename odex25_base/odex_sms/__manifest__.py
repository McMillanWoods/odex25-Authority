# -*- coding: utf-8 -*-
{
    'name': 'Odoo SMS Integration',
    'version': '1.0',
    'sequence': 4,
    'website': 'http://exp-sa.com',
    'license': 'GPL-3',
    'author': 'Expert Ltd',
    'summary': 'Odoo SMS Integration',
    'description': """
        Odoo odex_sms Integration
    """,
    'depends': ['base'],
    'data': ['security/ir.model.access.csv',
             'views/res_company_view.xml'
             ],
    'installable': True,
    'application': True,
}
