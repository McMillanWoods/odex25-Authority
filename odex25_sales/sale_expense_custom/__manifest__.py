# -*- coding: utf-8 -*-

{
    'name': "Sale Expense Custom",
    'version': "1.0",
    'category': "Sales",
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'summary': "Linked sale with Expense",
    'description': """Contains news linked sale with expense""",
    'depends': ['sale_expense', 'sale_custom'],
    'data': [
        'views/sale_order_views.xml',
        'views/hr_expense_view.xml',
    ],
    'installable': True,
    'application': False,
}
