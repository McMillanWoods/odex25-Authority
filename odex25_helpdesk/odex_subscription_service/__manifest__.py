# -*- coding: utf-8 -*-
{
    'name': "Odex Subscription Services",

    'summary': """An easy way to manage your subscriptions and recurring payments.""",

    'description': """
        This module is used to trigger any recurring type of invoice :
            - rent
            - Telephone/ internet subscription
            - Any other regular payment that needs a recurrent invoice.
            - Customer subcriptions
                - Which also comes with a customer portal to help your customers
                  to view and manager their subscription.
    """,
    'license' : 'AGPL-3',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'category': 'Uncategorized',
    'version': '1.1',
    'images': ['static/description/banner.png',],

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'analytic',
        'purchase',
        'sale',
        'sales_team',
        'portal',
    ],
    # always loaded
    'data': [
        'data/subscription_service_data.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'security/sale_subscription_security.xml',
        'views/assets.xml',
        'views/account_invoice_views.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/subscription_service_views.xml',
        'views/subscription_portal_templates.xml',
        'views/res_settings.xml',

    ],
}
