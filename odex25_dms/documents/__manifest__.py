# -*- coding: utf-8 -*-
{
    'name': "Documents",

    'summary': "Document management",

    'description': """
        Additional Libraries for Module MUK.
    """,

    'author': "Odoo",
    'category': 'Productivity/Documents',
    'sequence': 80,
    'version': '1.0',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'portal', 'web', 'attachment_indexation', 'digest'],

    # always loaded
    'data': [
        'views/assets.xml',
        'views/pdf.xml',
        'views/pdf_group_by_template.xml'
    ],

    'qweb': [
        "static/src/xml/*.xml",
        "static/src/owl/components/pdf_manager/pdf_manager.xml",
        "static/src/owl/components/pdf_page/pdf_page.xml",
        "static/src/owl/components/pdf_group_name/pdf_group_name.xml",
    ],

    'license': 'OEEL-1',
}
