# -*- coding: utf-8 -*-

{
    'name': "CRM Expense",
    'version': "1.0",
    'category': "Sales/CRM",
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'summary': "Linked CRM with Expense",
    'description': """Contains news linked crm with expense""",
    'depends': ['crm', 'hr_expense'],
    'data': [
        'views/crm_lead_views.xml',
        'views/hr_expense_view.xml',
    ],
    'installable': True,
    'application': False,
}
