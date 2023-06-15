# -*- coding: utf-8 -*-
{
    'name': "Project Custom",
    'summary': """Project Custom""",
    'description': """
Project Custom
    """,
    'category': 'Project',
    'version': '1.0',
    'depends': ['sale_timesheet','dms','base_odex','hr_timesheet_sheet'],
    'data': [
        'data/project_data.xml',
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'views/project_views.xml',
        'views/project_phase_view.xml',
        'views/project_time_plan_view.xml',
        'views/week_week_view.xml',
        'views/project_task_views.xml',
        'wizard/week_generation_wizard_views.xml',
    ],
    

    'auto_install': False,
}
