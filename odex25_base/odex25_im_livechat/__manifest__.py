# -*- coding: utf-8 -*-

{
    'name': "Odex25 Live chat",
    'version': "1.0",
    'category': 'Odex25 Website/Website',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'summary': "Advanced features for Live Chat",
    'description': """
Contains advanced features for Live Chat such as new views
    """,
    'depends': ['im_livechat', 'odex25_web_dashboard'],
    'data': [
        'views/im_livechat_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': ['im_livechat'],
}
