# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class private_budget_structure(models.Model):
#     _name = 'private_budget_structure.private_budget_structure'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100