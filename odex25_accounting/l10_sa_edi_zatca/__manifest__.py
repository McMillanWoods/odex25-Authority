# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo,
#    Copyright (C) 2022 dev: Abdullah Elyamani.
#    Mob. +20 1011002165
#    Email. abdullahelyamani@gmail.com
#
##############################################################################
{
    'name': "KSA E-Invoice Integration",

    'summary': """
        KSA Tax Authority Invoice Integration.
        """,

    'description': """
       This module integrate with the Zatca Portal to automatically sign and send your invoices to the tax Authority.
    """,

    'author': "Abdullah Elyamani",
    'website': "abdullahelyamani@gmail.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'account_edi', 'l10n_sa_invoice'],

    # always loaded
    'data': [
        'data/ubl_template.xml',
        # 'views/assets.xml',
        # 'views/eta_thumb_drive.xml',
        'views/account_move.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
