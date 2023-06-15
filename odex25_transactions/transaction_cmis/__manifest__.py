# -*- coding: utf-8 -*-
##############################################################################
#
#    Odex - Communications Management System.
#    Copyright (C) 2019 Expert Co. Ltd. (<http://exp-sa.com>).
#
##############################################################################
{
    'name': 'Communications Management DMS',
    'version': '1.0',
    'author': 'Expert Co. Ltd. - Sudan Team',
    'summary': 'Communications Management DMS',
    'description': """
Odex - Communications Management System DMS
========================================
Managing Communications Transcations DMS
    """,
    'website': 'http://www.exp-sa.com',
    'depends': ['exp_transaction_documents', 'cmis_field'],
    'data': [
        'views/internal_transaction.xml',
    ],
    'qweb' : [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
