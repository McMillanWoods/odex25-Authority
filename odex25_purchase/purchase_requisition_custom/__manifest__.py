# -*- coding: utf-8 -*-
{
    'name': 'Purchase Requisition Custom',
    'version': '1.1',
    'summary': 'Adding new Functionality on the Purchase Agreements',
    'sequence': -1,
    'description': """
        Adding new Functionalities in Purchase Agreements
    """,
    'data': [
        'security/category_groups.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'data/purchase_sequence.xml',
        'data/purchase_request_seq.xml',
        'data/mail_template.xml',
        'data/cron_data.xml',
        'wizards/convert_to_contract.xml',
        'views/purchase_requisition_custom.xml',
        'views/purchase_request.xml',
        'views/res_setting.xml',
        'views/vendor_type.xml',
        'reports/external_layout.xml',
        'reports/committee_meeting_minutes_report.xml',
        'views/budget_confirmation.xml',
    ],
    'depends': ['exp_analytic','stock', 'purchase','project_custom', 'purchase_requisition', 'zuhair_purchase', 'analytic','hr','account_budget_custom','purchase_stock'],
    # 'account_budget_custom', exp_budget_check
    'installable': True,
    'application': True,
}
