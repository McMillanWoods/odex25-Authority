{
    'name': 'HR Administrative Circulars And Decitions',
    'category': 'HR-Odex',
    'summary': 'Manages both Internaal and External Administrative Circulars And Decitions',
    'version': '1.0',
    'sequence': 4,
    'website': 'http://exp-sa.com',
    'license': 'GPL-3',
    'author': 'Expert Co. Ltd.',
    'depends': ['hr_base'],
    'data': [

        'security/ir.model.access.csv',
        'report/administrative_circular_decision_templates.xml',
        'views/administrative_circular_decision_report.xml',
        'views/administrative_circular_view.xml',
        'data/mail_template_data.xml',
    ],
    'installable': True,
    'application': True,
 }

