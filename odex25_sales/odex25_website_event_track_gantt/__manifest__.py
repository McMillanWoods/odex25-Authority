# -*- coding: utf-8 -*-

{
    'name': 'Enterprise Event Track',
    'category': 'Odex25 Marketing',
    'author': 'Expert Co. Ltd.',
    'website': 'http://www.exp-sa.com',
    'summary': 'Advanced Event Track Management',
    'version': '1.0',
    'description': """This module helps analyzing and organizing event tracks.
For that purpose it adds a gantt view on event tracks.""",
    'depends': ['website_event_track', 'odex25_web_gantt'],
    'auto_install': True,
    'data': [
        'views/event_event_views.xml',
        'views/event_track_views.xml',
    ],
}
