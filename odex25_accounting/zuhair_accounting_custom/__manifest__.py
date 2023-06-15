# -*- coding: utf-8 -*-
{
    "name": "Accounting Customize",
    "version": "14.0.1.0.0",
    "summary": "Accounting Customize for Zuhair Company",
    'license': 'AGPL-3',
    'category': 'Odex25 Accounting/Accounting',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    "depends": [
        'account',
        'account_fiscal_year',
        'branch',
    ],
    'data': [
        'security/account_security.xml',
        'security/ir.model.access.csv',
        'wizard/account_execution_guarantee_wizard_views.xml',
        'views/account_move_views.xml',
        'views/account_views.xml',
        'views/account_payment_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
}
