# -*- coding: utf-8 -*-
##############################################################################
#
#    Odex - Communications Management System.
#    Copyright (C) 2019 Expert Co. Ltd. (<http://exp-sa.com>).
#
##############################################################################
{
    'name': 'leave Transaction Management',
    'version': '1.0',
    'sequence': 4,
    'author': 'Expert Co. Ltd.',
    'category': 'Mailing',
    'summary': 'Correspondence Management System',
    'description': """
Odex - Communications Management System
========================================
Managing Communications Transcations in emplyee holdays flows
    """,
    'website': 'http://www.exp-sa.com',
    'depends': ['exp_transaction_documents'],
    'data': [
        'security/ir.model.access.csv',
        'views/leave.xml',
        'data/state_expired_corn.xml'
    ],
    'qweb' : [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
