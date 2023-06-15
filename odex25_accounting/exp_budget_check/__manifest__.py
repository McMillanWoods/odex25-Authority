# -*- coding: utf-8 -*-
{
    'name': "Check Budget",

    'summary': """
       """,

    'description': """
       Check budget in vendor bill
    """,
    'website': 'http://exp-sa.com',
    'license': 'GPL-3',
    'author': 'Expert Co. Ltd.',

    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'account_configuration',
        'account_budget_custom',
        'hr_expense_petty_cash',

    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/hr_expense_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
