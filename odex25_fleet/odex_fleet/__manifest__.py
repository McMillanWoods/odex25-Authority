# -*- coding: utf-8 -*-
{
    'name': "Odex Fleet",

    'summary': """
        Manage Fleet and Reports""",

    'description': """
Manage Fleet and Reports
    """,

    'author': "Expert Co Ltd",
    'website': "http://www.ex.com",
    'category': 'fleet',
    'version': '0.1',
    'depends': ['fleet','branch'],
    # 'exp_custody_petty_cash',
    # 'bi_odoo_multi_branch_hr'
    # 'hr_base'
    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'views/vehicle_view.xml',
        'views/vehicle_deleation_view.xml',
        'views/driver_view.xml',
        'views/maintenance_request_view.xml',
        'views/renew_view.xml',
        'views/config_view.xml',
        'views/account_config_view.xml',
        'data/cron_data.xml',
        'views/mail_template.xml',
        'wizards/fleet_view.xml',
        'reports/fleet_template.xml',
        'reports/maintains_template.xml',
        'reports/driver_template.xml',
        'reports/renew_template.xml',
        'reports/service_template.xml',
        'reports/maintains_purchase_request.xml',
        'reports/service_purchase_request.xml',
        'wizards/reject_reason.xml',
        'views/insurance_companies.xml',
        'views/infractions.xml',
        'wizards/reject_reason_infraction.xml',
        'views/driver_departments.xml',

    ]
}