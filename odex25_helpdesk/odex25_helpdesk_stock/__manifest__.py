# -*- coding: utf-8 -*-

{
    'name': 'Helpdesk Stock',
    'category': 'Odex25 Services/Helpdesk',
    'summary': 'Project, Tasks, Stock',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['odex25_helpdesk_sale', 'stock'],
    'auto_install': False,
    'description': """
Manage Product returns from helpdesk tickets
    """,
    'data': [
        'wizard/stock_picking_return_views.xml',
        'views/odex25_helpdesk_views.xml',
    ],
    'demo': ['data/odex25_helpdesk_stock_demo.xml'],
}
