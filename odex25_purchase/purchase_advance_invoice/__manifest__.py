# -*- coding: utf-8 -*-
{
    'name': "Purchase Advance Invoice",

    'summary': """
        Advance Invoice purchase""",

    'description': """
        Advance Invoice purchase
    """,

    'author': "Expert Co Ltd.",
    'website': "http://www.exp-sa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_make_invoice_advance_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}