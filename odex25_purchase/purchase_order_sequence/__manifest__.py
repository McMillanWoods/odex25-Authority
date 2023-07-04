# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

{
    'name': 'Different Sequences For Quotation / Purchase Order',
    'version': "1.0",
    "summary": """Different sequences for RFQs and Purchase Order.""",
    "description": """
This module allow to create different sequences for RFQs and Purchase Order
    """,
    'author': 'TidyWay',
    'website': 'http://www.tidyway.in',
    'category': 'Purchase Management',
    'depends': ["purchase"],
    'data': [
        'views/purchase_view.xml',
        'views/purchase_sequence.xml',
    ],
    'price': 20,
    'currency': 'EUR',
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'auto_install': False,
    'images': ['images/sequence.jpg'],
}
