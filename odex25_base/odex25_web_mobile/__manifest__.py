# -*- coding: utf-8 -*-


{
    'name': 'Mobile',
    'category': 'Odex25 Hidden',
    'author': 'Expert Co. Ltd.',
    'website': 'http://www.exp-sa.com',
    'summary': 'Odoo Mobile Core module',
    'version': '1.0',
    'description': """
        This module provides the core of the Odoo Mobile App.
        """,
    'depends': [
        'odex25_web',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'data': [
        'views/mobile_template.xml',
        'views/views.xml',
    ],
    'installable': True,
    #'auto_install': True,
}
