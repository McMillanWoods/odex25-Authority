# -*- coding: utf-8 -*-
##############################################################################
#
#    Odex - Communications Management System.
#    Copyright (C) 2017 Expert Co. Ltd. (<http://exp-sa.com>).
#
##############################################################################
{
    'name': 'Correspondence Traking (Mailing)',
    'version': '0.1',
    'sequence': 20,
    'author': 'Expert Co. Ltd.',
    'category': 'Mailing',
    'summary': 'Mailing <> Correspondence Traking',
    'description': """
Odex - Communications Management System - Link with Email
==========================================================

* Import  Transactions from email.
    """,
    'website': 'http://www.exp-sa.com',
    'depends': ['base', 'base_odex', 'mail','exp_transaction_documents'],
    'data': [
        'views/actions_and_menus.xml',
    ],
    'qweb': [
    ],
    'external_dependencies': {},
    'installable': True,
    'auto_install': False,
    'application': False,
}
