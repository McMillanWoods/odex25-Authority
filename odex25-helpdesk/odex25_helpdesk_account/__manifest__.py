# -*- coding: utf-8 -*-

{
    'name': 'Helpdesk Account',
    'category': 'Odex25 Services/Helpdesk',
    'summary': 'Project, Tasks, Account',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['odex25_helpdesk_sale', 'account'],
    'auto_install': False,
    'description': """
Create Credit Notes from Helpdesk tickets
    """,
    'data': [
        'wizard/account_move_reversal_views.xml',
        'views/odex25_helpdesk_views.xml',
    ],
}
