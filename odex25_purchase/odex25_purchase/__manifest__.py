# -*- coding: utf-8 -*-

{
    'name': "Purchase Dashboard",
    'version': "1.0",
    'category': 'Odex25 Inventory/Purchase',
    'author': 'Expert Co. Ltd.',
    'website': 'http://www.exp-sa.com',
    'summary': "Advanced Features for Purchase Management",
    'description': """
Contains advanced features for purchase management
    """,
    'depends': ['purchase', 'odex25_web_dashboard'],
    'data': [
        'report/purchase_report_views.xml',
    ],
    'demo': [
        'data/purchase_order_demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': ['purchase'],
}
