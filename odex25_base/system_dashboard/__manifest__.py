# -*- coding: utf-8 -*-
{
    'name': "System Dashboard - EXPERT",
    'summary': """
        This module allows you to configure dashboard for different  states or stages  for  specific model.""",

    'description': """
        This module allows you to configure dashboard for different users
        add state and its corresponding group which it will be visible ,
        depends on logged in user they can see records if it is on one state that they has access on
        there also a self service screen which employees can see their request in any model.""",

    'author': "Expert Co. Ltd., Sudan Team",
    # 'website': "http://www.yourcompany.com",
    'version': '0.1',
    'application':True,
    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/dashboard_view.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
}