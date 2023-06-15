# -*- coding: utf-8 -*-
##############################################################################
#
#    Odex - Communications Management System.
#    Copyright (C) 2019 Expert Co. Ltd. (<http://exp-sa.com>).
#
##############################################################################
{
    'name': 'Transaction Letters Managment',
    'version': '1.0',
    'sequence': 4,
    'author': 'Expert Co. Ltd. - Sudan Team',
    'category': '',
    'summary': 'Letters Managment',
    'description': """
Letters Managment
========================================
    """,
    'website': 'http://www.exp-sa.com',
    'depends': ['exp_transaction_documents'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/letters_view.xml',
        'reports/letter_template.xml',
    ],
    'qweb' : [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
