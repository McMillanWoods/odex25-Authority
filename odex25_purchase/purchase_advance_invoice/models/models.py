# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoiceCustom(models.Model):
    _inherit = 'account.move'


    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'qty_received', 'product_uom_qty', 'order_id.state')
    def _compute_qty_invoiced(self):
        
        res = super(AccountInvoiceCustom, self)._compute_qty_invoiced()
        for line in self:
            if line.product_id.purchase_method == 'purchase':
                qty = line.product_qty - line.qty_invoiced
                line.qty_to_invoice = qty
        return res



class PurchaseOrderCustom(models.Model):
    _inherit = 'purchase.order'

    
    def action_invoice_create(self, grouped=False, final=False):
        return self.purchase_order_change()