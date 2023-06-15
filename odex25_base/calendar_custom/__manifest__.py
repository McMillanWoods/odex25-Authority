{
    'name': 'Calendar Custom',  
    'depends': ['calendar', 'branch', 'odex25_helpdesk'],
    'data': [
        'security/ir.model.access.csv',
        'views/calendar_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
