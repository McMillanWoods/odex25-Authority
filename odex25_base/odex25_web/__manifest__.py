# -*- coding: utf-8 -*-


{
    'name': 'Odex25 Web',
    'category': 'Odex25 Hidden',
    'author': 'Expert Co. Ltd.',
    'website': 'http://www.exp-sa.com',
    'version': '1.0',
    'description':
        """
Odoo Enterprise Web Client.
===========================

This module modifies the web addon to provide Odex design and responsiveness.
        """,
    'depends': ['web'],
    #'auto_install': True,
    'data': [
        'views/webclient_templates.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
}
