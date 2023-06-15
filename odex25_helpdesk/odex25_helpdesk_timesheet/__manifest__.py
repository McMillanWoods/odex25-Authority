# -*- coding: utf-8 -*-

{
    'name': 'Helpdesk Timesheet',
    'category': 'Odex25 Services/Helpdesk',
    'summary': 'Project, Tasks, Timesheet',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['hr_timesheet', 'odex25_timesheet_grid', 'odex25_helpdesk'],
    'description': """
        - Allow to set project for Helpdesk team
        - Track timesheet for a task from a ticket
    """,
    'data': [
        'security/ir.model.access.csv',
        'security/odex25_helpdesk_timesheet_security.xml',
        'views/odex25_helpdesk_views.xml',
        'views/project_views.xml',
        'wizard/odex25_helpdesk_ticket_create_timesheet_views.xml',
        'data/odex25_helpdesk_timesheet_data.xml',
    ],
    'demo': ['data/odex25_helpdesk_timesheet_demo.xml'],
    'post_init_hook': '_odex25_helpdesk_timesheet_post_init'
}
