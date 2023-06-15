# -*- coding: utf-8 -*-
##############################################################################
#
#    Odex - Communications Management System.
#    Copyright (C) 2019 Expert Co. Ltd. (<http://exp-sa.com>).
#
##############################################################################
{
    'name': 'Communications Management',
    'version': '1.0',
    'sequence': 4,
    'author': 'Expert Co. Ltd.',
    'category': 'Mailing',
    'summary': 'Correspondence Management System',
    'description': """
Odex - Communications Management System
========================================
Managing Communications Transcations flows
    """,
    'website': 'http://www.exp-sa.com',
    'depends': ['base', 'base_odex', 'mail', 'html_text', 'project_custom', 'odex_sms'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/cm_data.xml',
        'data/ir_cron.xml',
        'views/entity.xml',
        'views/configuration.xml',
        'views/transcation_common_view.xml',
        'views/internal.xml',
        'views/incoming.xml',
        'views/outgoing.xml',
        'reports/transaction_details_report_template.xml',
        'reports/receiver_transaction_report_template.xml',
        # 'views/settings_config_view.xml',
        'views/actions_and_menus.xml',
        'wizard/reject_transaction_reson.xml',
        'wizard/forward_transaction.xml',
        'wizard/archive_transaction.xml',
        'wizard/transaction_reply_wizard.xml',
        'wizard/reopen_transaction_wizard.xml',
        'email_templates/internal_templates.xml',
        'email_templates/incoming_templates.xml',

    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
