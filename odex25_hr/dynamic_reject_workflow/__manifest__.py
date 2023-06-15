# -*- coding: utf-8 -*-
{
    'name': "Dynamic Reject Workflow",
    'description': """
        Dynamic Reject Workflow
    """,
    'category': 'ODEX HR',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['mail'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/reject_buttons.xml',
        'views/reject_workflow.xml',
        'wizard/reject_wizard.xml',
        'views/assets.xml',
    ],
}
