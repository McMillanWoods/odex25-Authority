# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api,_


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    # We keep this field for migration purpose
    # old_contract_id = fields.Many2one(
    #     'contract.contract', oldname='contract_id')
    contract_id = fields.Many2one(
        'contract.contract', string='Contract',
    )

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if self.env.context.get('create_installment'):
            self.env['line.contract.installment'].create({
                'name': _('Delivery installment'),
                'amount': self.env.context.get('default_installment_amount'),
                'due_date': vals.get('date_invoice') or fields.Date.today(),
                'tax_id': self.env.context.get('default_tax'),
                'state': 'invoiced',
                'invoice_id': res.id,
                'contract_id': self.env.context.get('default_contract_id'),
            })
        return res