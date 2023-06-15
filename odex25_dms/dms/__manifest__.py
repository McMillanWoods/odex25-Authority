# Copyright 2017-2019 MuK IT GmbH
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Document Management System",
    "summary": """Document Management System for Odoo""",
    "version": "14.0.4.0.0",
    "category": "Document Management",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/dms",
    "author": "MuK IT, Tecnativa, Odoo Community Association (OCA)",
    "depends": [
        'base',
        'web',
        'attachment_indexation',
        'digest',
        "web_drop_target",
        "mail",
        "http_routing",
        "portal",
        "mail_preview_base",
        "project",
        "board",
        'documents'
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "actions/file.xml",
        "data/documents_data.xml",
        "data/mail_templates.xml",
        "template/assets.xml",
        "template/onboarding.xml",
        "views/documents_views.xml",
        # 'views/assets.xml',
        'views/templates.xml',
        'views/activity_views.xml',
        "views/menu.xml",
        "views/tag.xml",
        "views/category.xml",
        # "views/dms_file.xml",
        "views/directory.xml",
        "views/attach.xml",
        "views/storage.xml",
        "views/settings_view.xml",
        "views/dms_access_groups_views.xml",
        "views/res_config_settings.xml",
        "views/dms_portal_templates.xml",
        'wizard/request_activity_views.xml',
    ],
    "qweb": ["static/src/xml/views.xml"],
    "images": ["static/description/banner.png"],
    "application": True,
}