# -*- coding: utf-8 -*-
{
    'name': "Marketing Automation",
    'version': "1.0",
    'summary': "Build automated mailing campaigns",
    'author': 'Expert Co. Ltd.',
    'website': 'http://www.exp-sa.com',
    'category': "ODEX25 Marketing/Marketing Automation",
    'sequence': 195,
    'depends': ['mass_mailing'],
    'data': [
        'security/odex25_marketing_automation_security.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/ir_actions_views.xml',
        'views/ir_model_views.xml',
        'views/odex25_marketing_automation_menus.xml',
        'wizard/marketing_campaign_test_views.xml',
        'views/link_tracker_views.xml',
        'views/mailing_mailing_views.xml',
        'views/mailing_trace_views.xml',
        'views/marketing_activity_views.xml',
        'views/marketing_participant_views.xml',
        'views/marketing_trace_views.xml',
        'views/marketing_campaign_views.xml',
        'data/ir_cron_data.xml',
    ],
    'demo': [
        'data/odex25_marketing_automation_demo.xml'
    ],
    'application': True,
    'uninstall_hook': 'uninstall_hook',
}
