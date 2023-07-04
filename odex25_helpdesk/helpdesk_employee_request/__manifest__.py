# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'EXP Helpdesk Employee Request',
    'summary': 'adding menu for employees to request tickets in helpdesk',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['odex25_helpdesk','odex25_helpdesk_timesheet'],
    'description': """
        Adding menu for employees to request tickets in helpdesk
    """,
    'auto_install': True,
    'data': [
        'data/helpdesk_data.xml',
        'security/helpdesk_timesheet_security.xml',
        'security/ir.model.access.csv',
        'views/helpdesk_views.xml',
    ],
    'license': '',
}
