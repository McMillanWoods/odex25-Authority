# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def action_view_expense(self):
        action = self.env["ir.actions.actions"]._for_xml_id("hr_expense.hr_expense_actions_my_unsubmitted")
        action['context'] = {
            'default_sale_order_id': self.id,
            'default_partner_id': self.partner_id.id,
        }
        action['domain'] = [('sale_order_id', '=', self.id)]
        return action