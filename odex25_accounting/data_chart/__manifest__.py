# -*- coding: utf-8 -*-
{
    'name': "data visualization",
    'version': '1.0',

    'summary': """
        add data visualization in  to odoo 
        this module is adding the ability to create and manage new table reports
        for a spacific model or a query based on data items
    """,

    'category': 'ODEX ACCOUNTING',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/data_chart_report_view.xml',
    ],
    'demo':[
        'data/demo.xml',
    ],
    'qweb': ["static/src/xml/data_chart_templates.xml"],


}
