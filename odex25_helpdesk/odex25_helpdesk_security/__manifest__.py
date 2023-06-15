# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'EXP Helpdesk Security',
    'category': 'Hidden',
    'summary': 'Ticket Security',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['odex25_helpdesk','odex25_helpdesk_reopen'],
    'description': """
        Ticket Security
    """,
    'auto_install': True,
    'data': [
        # 'data/helpdesk_data.xml',
        'security/helpdesk_security.xml',
        'security/ir.model.access.csv',
        'views/view.xml',
    ],
    'qweb': [
        "static/src/xml/template.xml",
    ],
    'license': '',
}
