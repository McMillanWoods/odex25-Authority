# -*- coding: utf-8 -*-
{
    'name': "Odex Online Tendering",

    'summary': """
        Online tendering For odex""",

    'description': """
        This Module is Designed to allow online tendering work smothly with other odex purchase modules
    """,

    'author': "Expert Company Ltd",
    'website': "http://www.exp-sa.com",

    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['online_tendering' , 'purchase_requisition_custom'],

    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    # # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}