# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
# from odoo.exceptions import Warning


class Entity(models.Model):
    _inherit = 'cm.entity'
    _description = 'for mange transaction in multi level'

    manager_entity = fields.Many2many(comodel_name='cm.entity', relation='manage_entity_rel', column1='manager_id',
                                      column2='entity_id', string='Owners of powers')
    need_multi_approve = fields.Boolean(string='Need Multi level Approve')


