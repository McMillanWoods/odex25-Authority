{
    'name': "Purchase Dashboard",
    'version': '11.0.1.0.0',
    'summary': """Purchase Custom Dashboard""",
    'category': 'Purchase',
    'author': 'Expert Co. Ltd.',
    'company': 'Expert Co. Ltd.',
    'website': "https://www.exp-sa.com",
    'depends': ['base', 'purchase'],
    # 'external_dependencies': {
    #     'python': ['pandas'],
    # },
    'data': [
        'views/dashboard_views.xml',
    ],
    'qweb': ["static/src/xml/*.xml"],
    'installable': True,
    'application': True,
}
