# -*- coding: utf-8 -*-

{
    'name': "Odex25 Project",
    'summary': """Bridge module for project and odex25""",
    'description': """
Bridge module for project and odex25
    """,
    'category': 'Odex25 Services/Project',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'version': '1.0',
    'depends': ['project', 'odex25_web_map', 'odex25_web_gantt'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/project_task_views.xml',
        'views/assets.xml',
    ],
    'auto_install': True,
}
