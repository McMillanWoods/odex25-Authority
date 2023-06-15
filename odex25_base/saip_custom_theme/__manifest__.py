# -*- coding: utf-8 -*-
{
    'name': "Saudi Authority custom theme",

    'summary': "Customization for backend themes built for Saudi Authority",

    'description': "Saudi Authority custom theme",

    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/resources.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}