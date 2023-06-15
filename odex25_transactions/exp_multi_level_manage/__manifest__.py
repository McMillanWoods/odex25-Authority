# -*- coding: utf-8 -*-
##############################################################################
#
#    Odex - Communications Management System.
#    Copyright (C) 2019 Expert Co. Ltd. (<http://exp-sa.com>).
#
##############################################################################
{
    'name': 'Multi-level Transaction Management',
    'version': '1.0',
    'sequence': 4,
    'author': 'Expert Co. Ltd.',
    'category': 'Mailing',
    'summary': 'Multi-level management of transactions',
    'description': """
Odex - Communications Management System
========================================
Multi-level management of transactions
    """,
    'website': 'http://www.exp-sa.com',
    'depends': ['exp_transaction_documents'],
    'data': [
        'views/extend_entity.xml',
    ],
    'qweb' : [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
