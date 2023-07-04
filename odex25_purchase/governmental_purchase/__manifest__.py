# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
{
    'name': 'Purchase Customizations For Governmental projects',
    'version': '1.1',
    'summary': 'Customize Purchase ',
    'sequence': -1,
    'description': """
    """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'data/mail_template.xml',
        'views/purchase_request_views.xml',
        'views/purchase_requisition_views.xml',
        'views/purchase_order_views.xml',
        'wizard/convert_to_contract.xml',
    ],
    'depends': ['purchase_requisition_custom', 'purchase_custom_vro'],
    # 'account_budget_custom',
    'installable': True,
    'application': False,
}
