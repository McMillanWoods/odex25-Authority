# -*- encoding: utf-8 -*-

{
    'name': 'No Expiration',
    'summary': 'No Expiration',
    'version': '1.0',
    'category': 'Base',
    'sequence': 10,
    'depends': [
        'base',
        'mail',
        'web_enterprise'
    ],
    'data': [
        "data/data.xml",
    ],
    'qweb': ['static/src/xml/expire.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
