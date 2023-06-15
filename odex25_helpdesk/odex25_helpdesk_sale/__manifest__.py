# -*- coding: utf-8 -*-

{
    'name': 'Helpdesk After Sales',
    'category': 'Odex25 Services/helpdesk',
    'summary': 'Project, Tasks, After Sales',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['odex25_helpdesk', 'sale_management'],
    'auto_install': True,
    'description': """
Manage the after sale of the products from helpdesk tickets.
    """,
    'data': [
        'views/odex25_helpdesk_views.xml',
    ],
    'demo': ['data/odex25_helpdesk_sale_demo.xml'],
}
