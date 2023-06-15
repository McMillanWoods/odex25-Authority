# -*- coding: utf-8 -*-
##############################################################################
#
#    Odex - Communications Management System.
#    Copyright (C) 2020 Expert Co. Ltd. (<http://exp-sa.com>).
#
##############################################################################
{
    'name' : 'C.M. Entity Sync',
    'version' : '0.1',
    'sequence' : 4,
    'author' : 'Expert Co. Ltd.',
    'category' : 'Mailing',
    'summary' : 'Correspondence Management, Entity Sync',
    'description' : """
Odex - Correspondence Management, Entity Syncronization
========================================================

Intercompanies entity syncronization
    """,
    'website': 'http://www.exp-sa.com',
    'depends': ['exp_transaction_documents'],
    'data': [
        'security/ir.model.access.csv',
        # data
        'data/data.xml',
        # views
        'views/entity_view.xml',
        'views/settings_view.xml',
        # wizards
        'wizards/inter_entity_wizard.xml',
        # actions amd menus
        'views/actions_and_menus.xml',
    ],
    'qweb' : [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
