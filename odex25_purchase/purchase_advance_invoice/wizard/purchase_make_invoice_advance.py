# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError,ValidationError


class purchaseAdvancePaymentInv(models.TransientModel):
    _name = "purchase.advance.payment.inv"
    _description = "purchases Advance Payment Invoice"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    # @api.model
    # def _get_advance_payment_method(self):
    #     if self._count() == 1:
    #         purchase_obj = self.env['purchase.order']
    #         order = purchase_obj.browse(self._context.get('active_ids'))[0]
    #         if all([line.product_id.invoice_policy == 'order' for line in order.order_line]) or order.invoice_count:
    #             return 'all'
    #     return 'delivered'

    @api.model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('purchase.default_deposit_product_id')
        return self.env['product.product'].browse(int(product_id))

    @api.model
    def _default_deposit_account_id(self):
        return self._default_product_id().property_account_income_id

    @api.model
    def _default_deposit_taxes_id(self):
        return self._default_product_id().taxes_id

    advance_payment_method = fields.Selection([
        # ('delivered', 'Invoiceable lines'),
        # ('all', 'Invoiceable lines (deduct down payments)'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)')
        ], string='What do you want to invoice?', required=True)
    product_id = fields.Many2one('product.product', string='Down Payment Product', domain=[('type', '=', 'service')],
        default=_default_product_id)
    count = fields.Integer(default=_count, string='# of Orders')
    amount = fields.Float('Down Payment Amount', digits=dp.get_precision('Account'), help="The amount to be invoiced in advance, taxes excluded.")
    deposit_account_id = fields.Many2one("account.account", string="Advance Payment Account", domain=[('deprecated', '=', False)],
        help="Account used for deposits", default=_default_deposit_account_id)
    deposit_taxes_id = fields.Many2many("account.tax", string="Customer Taxes", help="Taxes used for deposits", default=_default_deposit_taxes_id)

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            return {'value': {'amount': 0}}
        return {}

    @api.onchange('amount')
    def amount_validation(self):
        purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))[0]
        if self.advance_payment_method == "percentage" and (self.amount < 0 or self.amount >  100) :
            raise ValidationError(_("The Percent amount MUST be between 100 and 0"))
        elif self.amount > purchase_orders.amount_untaxed:
            raise ValidationError(_("you cann't Enter amount greater than po amount"))

    
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.move']
        ir_property_obj = self.env['ir.property']

        account_id = False
        if self.product_id.id:
            account_id = order.fiscal_position_id.map_account(self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id).id
        if not account_id:
            inc_acc = ir_property_obj._get('property_account_income_categ_id', 'product.category')
            account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.amount
            name = _('Down Payment')
        del context
        taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes).ids
        else:
            tax_ids = taxes.ids

        invoice = inv_obj.create({
            'name': order.name,
            # 'origin': order.name,
            'move_type': 'in_invoice',
            # 'reference': False,
            # 'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_id.id,
            'partner_shipping_id': order.partner_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                # 'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                # 'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'purchase_line_id': so_line.id,
                'tax_ids': [(6, 0, tax_ids)],
                # 'analytic_account_id': so_line.analytic_account_id.id or False,
            })],
            'currency_id': order.currency_id.id,
            # 'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'user_id': self.env.user.id,
            # 'comment': order.note,
        })
        # invoice._recompute_tax_lines()
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice

    
    def create_invoices(self):
        purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            purchase_orders.action_invoice_create()
        elif self.advance_payment_method == 'all':
            purchase_orders.action_invoice_create(final=True)
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('purchase.default_deposit_product_id', self.product_id.id)

            purchase_line_obj = self.env['purchase.order.line']
            for order in purchase_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.amount
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                else:
                    tax_ids = taxes.ids
                context = {'lang': order.partner_id.lang}
                so_line = purchase_line_obj.create({
                    'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_qty': 0.0,
                    'order_id': order.id,
                    # 'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'date_planned' : order.date_order,
                    'taxes_id': [(6, 0, tax_ids)],
                    # 'is_downpayment': True,
                })
                del context
                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return purchase_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _prepare_deposit_product(self):
        return {
            'name': 'Down payment',
            'type': 'service',
            'invoice_policy': 'order',
            'property_account_expense_id': self.deposit_account_id.id,
            'taxes_id': [(6, 0, self.deposit_taxes_id.ids)],
            'company_id': False,
        }
