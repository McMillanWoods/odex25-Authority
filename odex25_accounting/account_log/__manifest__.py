# -*- coding: utf-8 -*-
{
    'name': "Account Log",

    'summary': """
        Add chatter to accounts, taxes, journals, payment methods, bank accounts & currencies """,

    'description': """
    """,

    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'category': 'Odex25 Accounting/Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'odex25_account_budget', 'account_budget_custom', 'hr_expense_petty_cash'],

    # always loaded
    'data': [
        'views/account_chatter_view.xml',
    ]
}
