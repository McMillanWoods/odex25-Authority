# -*- coding: utf-8 -*-
##############################################################################
#
#    Odex - Communications Management System.
#    Copyright (C) 2019 Expert Co. Ltd. (<http://exp-sa.com>).
#
##############################################################################
{
    'name': 'Report Transaction Management',
    'version': '1.0',
    'sequence': 4,
    'author': 'Expert Co. Ltd.',
    'category': 'Report',
    'summary': 'Correspondence Management System',
    'description': """
Odex - Communications Management System
========================================
Managing Communications Transcations in emplyee holdays flows
    """,
    'website': 'http://www.exp-sa.com',
    'depends': ['exp_transaction_documents', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'report/close_transaction_report_template.xml',
        'report/forward_transaction_report_template.xml',
        'report/incoming_transaction_report_template.xml',
        'report/outgoing_transaction_report_template.xml',
        'report/outstanding_transaction_report_template.xml',
        'report/late_transaction_report_template.xml',
        'report/achievement_transaction_report_template.xml',
        'wizard/transaction_common_report_view.xml',
        'wizard/close_transaction_view_wiz.xml',
        'wizard/forward_transaction_report_wiz_view.xml',
        'wizard/incoming_transaction_report_wiz_view.xml',
        'wizard/late_transaction_report_wiz.xml',
        'wizard/outgoing_transaction_report_wiz_view.xml',
        'wizard/outstanding_transaction_report_view_wiz.xml',
        'wizard/achievement_transaction_report_view_wiz.xml',
    ],
    'qweb' : [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
