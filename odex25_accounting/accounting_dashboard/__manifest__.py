{
    'name': "Accounting Dashboard",
    'version': '11.0.1.0.0',
    'summary': """Accounting Custom Dashboard""",
    'category': 'Accounting',
    'author': 'Expert Co. Ltd.',
    'company': 'Expert Co. Ltd.',
    'website': "https://www.exp-sa.com",
    'depends': ['base', 'account','sale','report_xlsx'],
    # 'external_dependencies': {
    #     'python': ['pandas'],
    # },
    'data': [
        'security/ir.model.access.csv',

        'wizard/expense_report_wiz_view.xml',
        'wizard/expense_move_line_wiz_view.xml',
    ],

}
