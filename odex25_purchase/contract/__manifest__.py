# Copyright 2004-2010 OpenERP SA
# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# Copyright 2015 Domatix
# Copyright 2016-2018 Tecnativa - Carlos Dauden
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Recurring - Contracts Management',
    'version': '14.0..1.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "OpenERP SA, "
              "Tecnativa, "
              "LasLabs, "
              "Odoo Community Association (OCA)",
    'website': '',
    'depends': ['base', 'account', 'product','sale_management','sale','purchase_requisition_custom','purchase_stock'],
    "external_dependencies": {"python": ["dateutil"]},
    'data': [
        'security/ir.model.access.csv',
        'security/contract_security.xml',
        'report/report_contract.xml',
        'report/report_action.xml',
        'report/employee_contract_report_template_exp.xml',
        'report/contract_residual_installlments.xml',
        'report/contract_finaical_requests.xml',
        'report/installment_report.xml',
        'report/gernerl_contract_report.xml',
        'report/contract_details_report.xml',
        'report/contract_vendor_report.xml',
        'data/contract_cron.xml',
        'data/contract_renew_cron.xml',
        'data/supplier_contract_cron.xml',
        'data/mail_template.xml',
        'data/installment_contract_template.xml',
        'data/installment_cron.xml',
        'data/instalment_daily_cron.xml',
        'data/daily_installment_mail_template.xml',
        # 'data/installment_template.xml',
        'data/ir_sequence.xml',
        'views/abstract_contract_line.xml',
        'views/contract.xml',
        'views/contract_line.xml',
        'views/contract_template.xml',
        'views/contract_template_line.xml',
        'views/res_partner_view.xml',
        'views/contract_installment.xml',
        'views/contract_report_template.xml',
        'views/purchase_order.xml',
        'wizards/contract_line_wizard.xml',
        'wizards/installments_report.xml',
        'wizards/general_contract_report.xml',
        'wizards/contract_details_report.xml',
        'wizards/contract_vendor_report.xml',
        
    ],
    'installable': True,
}
