# -*- coding: utf-8 -*-
{
    'name' : 'Purchases Reports Customization',
    'version' : '1.1',
    'summary': 'Adding reports on the purchase requisition',
    'sequence': -1,
    'description': """
            this module will add some report at the purchase customization
    """,
    'data':[
    'security/ir.model.access.csv',
	'reports/report_template.xml',
	'wizard/purchase_general_report_wizard.xml',
	'reports/report_actions.xml',
	'reports/purchase_general_report.xml',
	'wizard/purchase_total_report_wizard.xml',
	'reports/purchase_total_report.xml',
	'wizard/employee_purchase_report_wizard.xml',
	'reports/employee_purchase_report.xml',
    'views/asset_custom.xml',
    'wizard/purchase_committee_report.xml',
    'reports/purchase_committe_report.xml',
    'views/backend_assets.xml',        ],
    'depends' : ['purchase_requisition_custom','hr'],
    'installable': True,
    'application': True,
}
