# -*- coding: utf-8 -*-

{
    'name': 'Helpdesk: Knowledge Base',
    'category': 'Odex25 Services/Helpdesk',
    'sequence': 58,
    'summary': 'Knowledge base for helpdesk based on Odoo Forum',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': [
        'website_forum',
        'odex25_website_helpdesk'
    ],
    'description': """
Website Forum integration for the helpdesk module
=================================================

    Allow your teams to have a related forum to answer customer questions.
    Transform tickets into questions on the forum with a single click.

    """,
    'data': [
        'views/helpdesk_templates.xml',
        'views/helpdesk_views.xml',
    ],
    'auto_install': True,
}
