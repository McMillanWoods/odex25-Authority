# -*- coding: utf-8 -*-

{
    'name': 'Website Helpdesk',
    'category': 'Hidden',
    'sequence': 57,
    'summary': 'Bridge module for helpdesk modules using the website.',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'description': 'Bridge module for helpdesk modules using the website.',
    'depends': [
        'odex25_helpdesk',
        'website',
        'odex_subscription_service',
    ],
    'data': [
        'views/assets.xml',
        'views/portal_user_views.xml',
        'views/helpdesk_views.xml',
        'views/helpdesk_templates.xml',
    ],
}
