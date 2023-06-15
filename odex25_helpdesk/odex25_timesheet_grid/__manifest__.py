# -*- coding: utf-8 -*-
{
    'name': "Timesheets",
    'summary': "Track employee time on tasks",
    'description': """
* Timesheet submission and validation
* Activate grid view for timesheets
    """,
    'version': '1.0',
    'depends': ['odex25_web_grid', 'hr_timesheet', 'odex25_timer'],
    'category': 'Odex25 Services/Timesheets',
    'sequence': 65,
    'data': [
        'data/mail_data.xml',
        'security/timesheet_security.xml',
        'security/ir.model.access.csv',
        'views/hr_timesheet_views.xml',
        'views/res_config_settings_views.xml',
        'views/assets.xml',
        'wizard/timesheet_merge_wizard_views.xml',
    ],
    'demo': [
        'data/odex25_timesheet_grid_demo.xml',
    ],
    'qweb': [
        'static/src/xml/odex25_timesheet_grid.xml',
        'static/src/xml/timer_m2o.xml',
    ],
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'auto_install': ['odex25_web_grid', 'hr_timesheet'],
    'application': True,
    'pre_init_hook': 'pre_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
