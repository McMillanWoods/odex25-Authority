{
    'name': "Contract Dashboard",
    'version': '11.0.1.0.0',
    'summary': """Contracts Custom Dashboard""",
    'category': 'Purchase',
    'author': 'Expert Co. Ltd.',
    'company': 'Expert Co. Ltd.',
    'website': "https://www.exp-sa.com",
    'depends': ['base', 'contract'],
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
