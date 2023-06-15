# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    contract_id = fields.Many2one(
        'contract.contract', string='Contract',
    )

    # @api.model
    # def default_get(self, fields):
    #     rec = super(AccountPayment, self).default_get(fields)
    #
    #     context = dict(self._context or {})
    #     active_id = context.get('active_id')
    #     contract_id = self.env['contract.contract'].search([('id', '=', active_id)])
    #     if contract_id:
    #         rec['payment_type'] = 'outbound'
    #         rec['communication'] = contract_id.name
    #         rec['partner_id'] = contract_id.partner_id.id
    #         rec['amount'] = contract_id.with_tax_amount
    #     return rec
