# -*- coding: utf-8 -*-
{
    'name': 'Sign',
    'version': '1.0',
    'category': 'Odex25 Sales/Sign',
    'sequence': 105,
    'summary': "Send documents to sign online and handle filled copies",
    'description': """
Sign and complete your documents easily. Customize your documents with text and signature fields and send them to your recipients.\n
Let your customers follow the signature process easily.
    """,
    'author': "Expert Co. Ltd.",
    'website': "http://www.exp-sa.com",
    'depends': ['mail', 'attachment_indexation', 'portal', 'sms'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sign_data.xml',
        'views/sign_template_views_mobile.xml',
        'wizard/sign_send_request_views.xml',
        'wizard/sign_template_share_views.xml',
        'wizard/sign_request_send_copy_views.xml',
        'views/sign_request_templates.xml',
        'views/sign_template_templates.xml',
        'views/sign_request_views.xml',
        'views/sign_template_views.xml',
        'views/sign_log_views.xml',
        'views/sign_portal_templates.xml',
        'views/res_users_views.xml',
        'views/res_partner_views.xml',
        'views/sign_pdf_iframe_templates.xml',
        'report/sign_log_reports.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'demo': [
        'data/sign_demo.xml',
    ],
    'application': True,
    'installable': True,
}
