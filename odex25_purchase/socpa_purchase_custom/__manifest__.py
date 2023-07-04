# -*- coding: utf-8 -*-
{
    'name': "SOCPA Purchase",

    'summary': """
       This module Is Custom version of ODex Purchase""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Expert Co.ltd",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase_requisition_custom', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
}
