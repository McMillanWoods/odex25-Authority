# -*- coding: utf-8 -*-

{
    'name': 'Mail Enterprise',
    'category': 'Odex25 Productivity/Discuss',
    'author': 'Expert Co. Ltd.',
    'website': 'http://www.exp-sa.com',
    'depends': ['mail', 'odex25_web_mobile'],
    'description': """
Bridge module for mail and enterprise
=====================================

Display a preview of the last chatter attachment in the form view for large
screen devices.
""",
    'data': [
        'views/odex25_mail_templates.xml',
    ],
    'qweb': [
        'static/src/bugfix/bugfix.xml',
        'static/src/xml/odex25_mail.xml',
    ],
    #'auto_install': True,
}
