# -*- coding: utf-8 -*-
{
    'name': 'Odex Sale Contracts',
    'version': '14.0..1.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "EXP SA",
    'website': '',
    'depends': ['base', 'account', 'product','sale_management','sale','contract'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/sale_order.xml',
        'views/contract.xml',
    ],
    'installable': True,
}
