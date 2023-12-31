# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PaymentToken(models.Model):
    _name = 'payment.token'
    _inherit = 'payment.token'

    def get_linked_records(self):
        res = super(PaymentToken, self).get_linked_records()

        for token in self:
            subscriptions = self.env['sale.subscription'].search([('payment_token_id', '=', token.id)])
            for sub in subscriptions:
                res[token.id].append({
                    'description': subscriptions._description,
                    'id': sub.id,
                    'name': sub.name,
                    'url': '/my/subscription/' + str(sub.id) + '/' + str(sub.uuid)})

        return res


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    renewal_allowed = fields.Boolean(compute="_compute_renewal_allowed", store=False, help="Technical field used to control the renewal flow based on the transaction's state.")

    @api.depends('state')
    def _compute_renewal_allowed(self):
        for tx in self:
            tx.renewal_allowed = tx.state in ['done', 'authorized']
