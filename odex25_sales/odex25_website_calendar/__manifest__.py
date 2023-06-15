# -*- coding: utf-8 -*-


{
    'name': 'Appointments',
    'version': '1.0',
    'category': 'Odex25 Marketing/Online Appointment',
    'sequence': 215,
    'summary': 'Schedule appointments with clients',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'description': """
Allow clients to Schedule Appointments through your Website
-------------------------------------------------------------

""",
    'depends': ['calendar_sms', 'odex25_website', 'hr'],
    'data': [
        'data/odex25_website_calendar_data.xml',
        'views/calendar_views.xml',
        'views/calendar_appointment_views.xml',
        'views/odex25_website_calendar_templates.xml',
        'security/odex25_website_calendar_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'data/odex25_website_calendar_demo.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
