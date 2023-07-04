# -*- coding: utf-8 -*-
{
    'name': "Purchase Custom VRO",

    'author': "Expert CO Ltd",
    'website': "http://www.exp-sa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'product', 'purchase_requisition_stock', 'purchase_requisition_custom',
                'socpa_purchase_custom', 'account_budget_custom'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/stock_picking_type_data.xml',
        'wizards/stock_picking_cancel_reason_wiz_views.xml',
        'wizards/requistion_refues.xml',
        'views/purchase_order_views.xml',
        'views/purchase_request_views.xml',
        'views/purchase_requisition_views.xml',
        'views/stock_picking_views.xml',
        'views/res_partner.xml',
        'views/product.xml',
        'views/company.xml',
        # 'reports/external_layout.xml',
        'reports/custom_po_report.xml',
        'reports/goods_received_note_report.xml',
    ],
}
