# -*- coding: utf-8 -*-

{
    'name': "Events Organization Add-on",
    'summary': "Add views and tweaks on event",
    'description': """This module helps for analyzing event registrations.
For that purposes it adds

  * a cohort analysis on attendees;
  * a gantt view on events;

    """,
    'category': 'Odex25 Marketing/Events',
    'author': 'Expert Co. Ltd.',
    'website': 'http://www.exp-sa.com',
    'depends': ['event', 'odex25_web_cohort', 'odex25_web_gantt', 'odex25_web_map'],
    'data': [
        'views/event_event_views.xml',
        'views/event_registration_views.xml',
    ],
    'auto_install': True,
}
