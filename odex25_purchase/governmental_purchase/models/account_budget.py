# -*- coding: utf-8 -*-
from odoo import fields, models


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"
    # Added new
    reserve = fields.Float(string='Reserve Amount', tracking=True)
    initial_reserve = fields.Float(string='Initial Reserve Amount', tracking=True)
    confirm = fields.Float(string='Confirm Amount')
    year_end = fields.Boolean(compute="get_year_end")
