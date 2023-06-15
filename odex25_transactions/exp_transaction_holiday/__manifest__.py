# -*- coding: utf-8 -*-
##############################################################################
#
#    Odex - Communications Management System.
#    Copyright (C) 2020 Expert Co. Ltd. (<http://exp-sa.com>).
#
##############################################################################
{
    'name': 'Transaction Holiday Management',
    'version': '1.0',
    'sequence': 4,
    'author': 'Expert Co. Ltd. - Sudan Team',
    'category': '',
    'summary': 'Holiday Management',
    'description': """
Odex - Communications Management System
========================================
dayoff & public holiday management of transactions
    """,
    'website': 'http://www.exp-sa.com',
    'depends': ['exp_transaction_documents'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/transaction_holiday.xml',
    ],
    'qweb' : [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
