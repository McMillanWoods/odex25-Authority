# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    @api.model
    def default_get(self, fields):
        result = super(AccountMoveReversal, self).default_get(fields)
        ticket_id = result.get('odex25_helpdesk_ticket_id')
        if ticket_id and 'reason' in fields:
            result['reason'] = _('Helpdesk Ticket #%s', ticket_id)
        return result

    odex25_helpdesk_ticket_id = fields.Many2one('odex25_helpdesk.ticket')
    odex25_helpdesk_sale_order_id = fields.Many2one('sale.order', related="odex25_helpdesk_ticket_id.sale_order_id", string='Sales Order')
    suitable_move_ids = fields.Many2many('account.move', compute='_compute_suitable_moves')

    @api.depends('odex25_helpdesk_ticket_id.sale_order_id.invoice_ids', 'odex25_helpdesk_ticket_id.partner_id.commercial_partner_id')
    def _compute_suitable_moves(self):
        for r in self:
            domain = [('state', '=', 'posted'), ('move_type', '=', 'out_invoice')]
            if r.odex25_helpdesk_ticket_id.sale_order_id:
                domain.append(('id', 'in', r.odex25_helpdesk_ticket_id.sale_order_id.invoice_ids.ids))
            elif r.odex25_helpdesk_ticket_id.partner_id:
                domain.append(('partner_id', 'child_of', r.odex25_helpdesk_ticket_id.partner_id.commercial_partner_id.id))

            r.suitable_move_ids = self.env['account.move'].search(domain)._origin

    def reverse_moves(self):
        # OVERRIDE
        res = super(AccountMoveReversal, self).reverse_moves()

        if self.odex25_helpdesk_ticket_id:
            self.odex25_helpdesk_ticket_id.invoice_ids |= self.new_move_ids

        return res
