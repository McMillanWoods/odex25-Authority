# -*- coding: utf-8 -*-

{
    'name': 'Web Gantt',
    'category': 'Hidden',
    'description': """
Odoo Web Gantt chart view.
=============================

""",
    'author': 'Expert Co. Ltd.',
    'website': 'http://www.exp-sa.com',
    'version': '2.0',
    'depends': ['web'],
    'data' : [
        'views/odex25_web_gantt_templates.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'auto_install': True,
}
