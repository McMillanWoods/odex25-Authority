# -*- coding: utf-8 -*-
{
    'name': "ZFP Helpdesk Customization",
    'version': '1.3',
    'category': 'Odex25 Services/helpdesk',
    'sequence': 130,
    'summary': 'Add new customization to ZFP Helpdesk',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['hr','odex25_helpdesk'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/zfp_config_setting.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
