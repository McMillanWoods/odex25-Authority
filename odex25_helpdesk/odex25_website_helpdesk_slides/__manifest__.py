# -*- coding: utf-8 -*-

{
    'name': 'Website Slides Helpdesk',
    'category': 'Odex25 Services/Helpdesk',
    'sequence': 58,
    'summary': 'Ticketing, Support, Slides',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': [
        'odex25_website_helpdesk',
        'website_slides',
    ],
    'description': """
Website Slides integration for the helpdesk module
==================================================

    Add slide presentations to your team so customers seeking help can see them those before submitting new tickets.

    """,
    'data': [
        'views/helpdesk_views.xml',
        'views/helpdesk_templates.xml',
    ],
    'auto_install': True,
}
