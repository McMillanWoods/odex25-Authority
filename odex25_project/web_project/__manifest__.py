# -*- coding: utf-8 -*-
{
    'name': "Project Gantt Base",
    'summary': """base Module For Gantt Chart Module""",
    'description': """
base Module For Gantt Chart Module
    """,
    'category': 'Services/Project',
    'version': '1.0',
    'depends': ['project'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/project_task_views.xml',
        "views/res_config_settings.xml",
        "views/res_partner_views.xml",
        'views/web_gantt_templates.xml',
        'views/assets.xml',
    ],
    'qweb': [
        'static/web_gantt/src/xml/*.xml',
        "static/web_map/src/xml/map.xml"
    ],

    'auto_install': False,
}
