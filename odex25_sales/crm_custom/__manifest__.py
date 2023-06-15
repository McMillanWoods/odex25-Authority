# -*- coding: utf-8 -*-

{
    'name': "CRM Custom",
    'version': "1.0",
    'category': "Sales/CRM",
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'summary': "New features for CRM",
    'description': """Contains new features for CRM such as new views""",
    'depends': ['crm', 'project_custom'],
    'data': [
        'views/crm_lead_views.xml',
        'views/menu_views.xml',
        'views/product_service_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
}
