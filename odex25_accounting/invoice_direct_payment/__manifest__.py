# -*- coding: utf-8 -*-
{
    'name': "Invoice Direct Payment",
    'summary': """
        Activate cash base payment in supplier invoice. 
    """,
    'description': """
    """,
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'category': 'ODEX ACCOUNTING',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['purchase_custom_vro','private_budget_structure'],
    # always loaded
    'data': [
        'data/invoice_data.xml',
        'security/invoice_security_groups.xml',
        'security/ir.model.access.csv',
        'report/payment_receipt_template.xml',
        'report/invoice_receipt_template.xml',
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',
        'views/account_budget_view.xml',
    ]
}
