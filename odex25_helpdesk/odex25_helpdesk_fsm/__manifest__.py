# -*- coding: utf-8 -*-
{
    'name': "Helpdesk FSM",
    'summary': "Allow generating fsm tasks from ticket",
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'description': """
        Convert Helpdesk tickets to field service tasks.
    """,
    'category': 'Odex25 Services/Helpdesk',
    'depends': ['odex25_helpdesk', 'odex25_industry_fsm'],
    'data': [
        'security/ir.model.access.csv',
        'views/odex25_helpdesk_views.xml',
        'views/project_task_views.xml',
        'wizard/create_task_views.xml',
    ],
    'demo': ['data/odex25_helpdesk_fsm_demo.xml'],
    'auto_install': True,
}