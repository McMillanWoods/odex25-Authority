


from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        modules = self.env['ir.module.module'].sudo().search([('state', '=', 'installed'),
                                                              ('name', '=', 'contract')])
        if modules:
            self.contract_id = self.purchase_id.contract_id.id
        super(AccountInvoice, self).purchase_order_change()