# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'EXP Helpdesk Employee Request',
    'summary': 'adding menu for employees to request tickets in helpdesk',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['odex25_helpdesk'],
    'description': """
        Adding menu for employees to request tickets in helpdesk
    """,
    'auto_install': True,
    'data': [
        'security/helpdesk_timesheet_security.xml',
        'security/ir.model.access.csv',
        'views/help_request_view.xml',
    ],
    'license': '',
}
