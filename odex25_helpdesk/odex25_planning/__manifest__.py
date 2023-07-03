# -*- coding: utf-8 -*-

{
    'name': "Planning",
    'summary': """Manage your employees' schedule""",
    'description': """
    Schedule your teams and employees with shift.
    """,
    'category': 'Odex25 Human Resources/Planning',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'sequence': 130,
    'version': '1.0',
    'depends': ['hr', 'odex25_web_gantt', 'digest', 'odex25_hr_gantt'],
    'data': [
        'security/planning_security.xml',
        'security/ir.model.access.csv',
        'data/digest_data.xml',
        'wizard/planning_send_views.xml',
        'wizard/slot_planning_select_send_views.xml',
        'views/assets.xml',
        'views/hr_views.xml',
        'views/planning_template_views.xml',
        'views/planning_views.xml',
        'views/planning_report_views.xml',
        'views/res_config_settings_views.xml',
        'views/planning_templates.xml',
        'data/planning_cron.xml',
        'data/mail_data.xml',
    ],
    'demo': [
        'data/planning_demo.xml',
    ],
    'application': True,
    'qweb': [
        'static/src/xml/planning_gantt.xml',
    ]
}
