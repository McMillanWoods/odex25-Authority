# -*- coding: utf-8 -*-
{
    'name': 'Odex Global Discount',
    'version': '14.0.0.1',
    'category': 'Sales',
    'sequence': 18,
    'summary': 'Global discount for retail process',
    'description': """
    Global discount for sale,purchase,invoice with ability to apply discount after&before taxes and apply discount on line and whole record
""",

    'depends': ['base', 'sale', 'sale_management', 'account', 'purchase', 'stock'],
    'data': [
        'views/account_move_view.xml',
        'views/account_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'wizard/res_config_setting_view.xml',
        'report/inherit_sale_report.xml',
        'report/inherit_account_report.xml',
        'report/inherit_purchase_report.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
