# -*- coding: utf-8 -*-

{
    'name': 'Website IM Livechat Helpdesk',
    'category': 'Odex25 Services/Helpdesk',
    'sequence': 58,
    'summary': 'Ticketing, Support, Livechat',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': [
        'odex25_website_helpdesk',
        'website_livechat',
    ],
    'description': """
Website IM Livechat integration for the helpdesk module
=======================================================

Features:

    - Have a team-related livechat channel to answer your customer's questions.
    - Create new tickets with ease using commands in the channel.

    """,
    'data': [
        'views/helpdesk_view.xml',
    ],
    'auto_install': True,
}
