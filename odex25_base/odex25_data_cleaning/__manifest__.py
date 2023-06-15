# -*- coding: utf-8 -*-

{
    'name': 'Data Cleaning',
    'version': '1.0',
    'category': 'Odex25 Productivity/Data Cleaning',
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'sequence': 135,
    'summary': """Easily format text data across multiple records. Find duplicate records and easily merge them.""",
    'description': """Easily format text data across multiple records. Find duplicate records and easily merge them.""",
    'depends': ['web', 'mail', 'phone_validation'],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/odex25_data_cleaning_model_views.xml',
        'views/odex25_data_cleaning_rule_views.xml',
        'views/odex25_data_cleaning_record_views.xml',
        'views/odex25_data_cleaning_views.xml',
        'views/odex25_data_cleaning_templates.xml',
        'data/odex25_data_cleaning_data.xml',
        'data/odex25_data_cleaning_cron.xml',
    ],
    'qweb': [
        'static/src/xml/odex25_data_cleaning.xml'
    ],
    'installable': True,
    'application': True,
}
