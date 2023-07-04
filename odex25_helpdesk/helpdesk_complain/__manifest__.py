# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'EXP Helpdesk Complains',
    'summary': 'adding complains feature in the helpdesk ticket system',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['odex25_helpdesk'],
    'description': """
        ODEX system is over than 200+ modules developed by love of Expert Company, based on ODOO system
        .to effectively suite's Saudi and Arabic market needs.It is the first Arabic open source ERP and all-in-one solution 
    """,
    'auto_install': True,
    'data': [
        'security/complain_security.xml',
        'security/ir.model.access.csv',
        'views/helpdesk_sla_views.xml',
        'data/ticket_portal.xml',
        'data/complain_email_template.xml',
    ],
    'license': '',
}
