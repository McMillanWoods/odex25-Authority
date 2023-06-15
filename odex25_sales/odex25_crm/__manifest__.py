# -*- coding: utf-8 -*-

{
    'name': "Odex25 CRM",
    'version': "1.0",
    'category': "ODEX25 Sales/CRM",
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'summary': "Advanced features for CRM",
    'description': """
Contains advanced features for CRM such as new views
    """,
    'depends': ['crm', 'odex25_web_dashboard', 'odex25_web_cohort', 'odex25_web_map'],
    'data': [
        'views/crm_lead_views.xml',
        'views/assets.xml',
        'report/crm_activity_report_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': ['crm'],
}
