# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"


    sale_order_id = fields.Many2one('sale.order', store=True, string='Proposal', readonly=False, tracking=True,
    	states={'approved': [('readonly', True)], 'done': [('readonly', True)], 'refused': [('readonly', True)]},
    	# NOTE: only confirmed SO can be selected, but this domain in activated throught the name search with the `sale_expense_all_order`
    	# context key. So, this domain is not the one applied.
    	help="If the product has an expense policy, it will be reinvoiced on this sales order")


    @api.depends('can_be_reinvoiced')
    def _compute_sale_order_id(self):

    	return