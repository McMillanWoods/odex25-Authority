# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    department_id = fields.Many2one('hr.department', 'Business Unit')

