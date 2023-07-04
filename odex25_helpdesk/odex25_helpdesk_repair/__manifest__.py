# -*- coding: utf-8 -*-

{
    'name': 'Helpdesk Repair',
    'category': 'Odex25 Services/Helpdesk',
    'summary': 'Project, Tasks, Repair',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['odex25_helpdesk_stock', 'repair'],
    'auto_install': False,
    'description': """
Repair Products from Helpdesk tickets
    """,
    'data': [
        'views/odex25_helpdesk_views.xml',
        'views/repair_views.xml',
    ],
    'demo': ['data/odex25_helpdesk_repair_demo.xml'],
}
