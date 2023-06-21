# -*- coding: utf-8 -*-

{
    'name': 'Helpdesk',
    'version': '1.3',
    'category': 'Odex25 Services/helpdesk',
    'sequence': 110,
    'summary': 'Track, prioritize, and solve customer tickets',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': [
        'base_setup',
        'mail',
        'utm',
        'rating',
        'web_tour',
        'resource',
        'portal',
        'digest',
    ],
    'description': """
Odex25 helpdesk - Ticket Management App
================================

Features:

    - Process tickets through different stages to solve them.
    - Add priorities, types, descriptions and tags to define your tickets.
    - Use the chatter to communicate additional information and ping co-workers on tickets.
    - Enjoy the use of an adapted dashboard, and an easy-to-use kanban view to handle your tickets.
    - Make an in-depth analysis of your tickets through the pivot view in the reports menu.
    - Create a team and define its members, use an automatic assignment method if you wish.
    - Use a mail alias to automatically create tickets and communicate with your customers.
    - Add Service Level Agreement deadlines automatically to your tickets.
    - Get customer feedback by using ratings.
    - Install additional features easily using your team form view.

    """,
    'data': [
        'security/odex25_helpdesk_security.xml',
        'security/ir.model.access.csv',
        'data/digest_data.xml',
        'data/mail_data.xml',
        # 'data/odex25_helpdesk_data.xml',
        'views/odex25_helpdesk_views.xml',
        'views/odex25_helpdesk_views.xml',
        'views/zfp_config_setting.xml',
        'views/odex25_helpdesk_team_views.xml',
        'views/assets.xml',
        'views/digest_views.xml',
        'views/odex25_helpdesk_portal_templates.xml',
        # 'views/res_partner_views.xml',
        'views/mail_activity_views.xml',
        'report/odex25_helpdesk_sla_report_analysis_views.xml',
    ],
    'qweb': [
        "static/src/xml/odex25_helpdesk_team_templates.xml",
    ],
    # 'demo': ['data/odex25_helpdesk_demo.xml'],
    'application': True,
}
