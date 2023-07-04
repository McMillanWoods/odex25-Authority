# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'EXP Helpdesk SLA Escalation Reminder',
    'category': 'Hidden',
    'summary': 'Reminder in SLA Policy to reminde the team leader of the task depending on configuration',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['odex25_helpdesk'],
    'description': """
        Reminder in SLA Policy to reminde the team leader of the task depending on configuration
    """,
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'data/reminder_cron.xml',
        'data/reminder_templates.xml',
        'views/helpdesk_sla_views.xml',
    ],
    'license': '',
}
