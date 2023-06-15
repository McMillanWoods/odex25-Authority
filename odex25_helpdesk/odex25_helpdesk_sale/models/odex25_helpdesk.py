# -*- coding: utf-8 -*-

from odoo import api, fields, models


class odex25_helpdeskTicket(models.Model):
    _inherit = 'odex25_helpdesk.ticket'

    commercial_partner_id = fields.Many2one(related='partner_id.commercial_partner_id')
    sale_order_id = fields.Many2one('sale.order', string='Ref. Sales Order',
        domain="""[
            '|', (not commercial_partner_id, '=', 1), ('partner_id', 'child_of', commercial_partner_id or []),
            ('company_id', '=', company_id)]""",
        groups="sales_team.group_sale_salesman,account.group_account_invoice",
        help="Reference of the Sales Order to which this ticket refers. Setting this information aims at easing your After Sales process and only serves indicative purposes.")

    def copy(self, default=None):
        if not self.env.user.has_group('sales_team.group_sale_salesman') and not self.env.user.has_group('account.group_account_invoice'):
            if default is None:
                default = {'sale_order_id': False}
            else:
                default.update({'sale_order_id': False})
        return super(odex25_helpdeskTicket, self).copy(default=default)
