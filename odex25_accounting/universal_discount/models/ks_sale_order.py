# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class KsGlobalDiscountSales(models.Model):
    _inherit = "sale.order"

    ks_apply_global_discount = fields.Selection([('after', 'After Tax'), ('before', 'Before Tax')],
                                               string='Apply Discount', readonly=True,
                                               states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    ks_global_discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
                                               string='Universal Discount Type',
                                               readonly=True,
                                               states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                               default='percent')
    ks_global_discount_rate = fields.Float('Universal Discount',
                                           readonly=True,
                                           states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    ks_amount_discount = fields.Monetary(string='Universal Discount', readonly=True, compute='_amount_all', store=True,
                                         track_visibility='always')
    ks_enable_discount = fields.Boolean(compute='ks_verify_discount')

    @api.depends('company_id.ks_enable_discount')
    def ks_verify_discount(self):
        for rec in self:
            rec.ks_enable_discount = rec.company_id.ks_enable_discount

    @api.depends('order_line.price_total', 'ks_global_discount_rate', 'ks_global_discount_type','ks_apply_global_discount')
    def _amount_all(self):
        res = super(KsGlobalDiscountSales, self)._amount_all()
        for rec in self:
            if not ('ks_global_tax_rate' in rec):
                rec.ks_calculate_discount()
        return res

    # @api.multi
    def _prepare_invoice(self):
        res = super(KsGlobalDiscountSales, self)._prepare_invoice()
        for rec in self:
            res['ks_global_discount_rate'] = rec.ks_global_discount_rate
            res['ks_global_discount_type'] = rec.ks_global_discount_type
            res['ks_apply_global_discount'] = rec.ks_apply_global_discount
            res['ks_sales_discount_account'] = rec.company_id.ks_sales_discount_account
            res['ks_apply_global_discount'] = rec.ks_apply_global_discount
            res['invoice_date'] = fields.Date.context_today(self)
        return res

    # @api.multi
    def ks_calculate_discount(self):
        for rec in self:
            if rec.ks_global_discount_type == "amount":
                rec.ks_amount_discount = rec.ks_global_discount_rate if rec.amount_untaxed > 0 else 0

            elif rec.ks_global_discount_type == "percent":
                if rec.ks_global_discount_rate != 0.0:
                    rec.ks_amount_discount = (rec.amount_untaxed + rec.amount_tax) * rec.ks_global_discount_rate / 100
                else:
                    rec.ks_amount_discount = 0
            elif not rec.ks_global_discount_type:
                rec.ks_amount_discount = 0
                rec.ks_global_discount_rate = 0

            total_tax = 0
            total_amount = sum(line.price_subtotal for line in rec.order_line)
            for line in rec.order_line:
                if rec.ks_amount_discount:
                    if rec.ks_global_discount_type == 'amount':
                        percent = line.price_subtotal / total_amount
                        discount_val = rec.ks_amount_discount * percent
                        price = line.price_subtotal - discount_val
                    else:
                        price = line.price_subtotal - (line.price_subtotal * (rec.ks_global_discount_rate / 100))
                else:
                    price = line.price_subtotal
                taxes = line.tax_id.compute_all(
                    price,
                    line.order_id.currency_id,
                    line.product_uom_qty,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id)
                total_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
             
            ks_amount_discount = rec.ks_amount_discount
            if rec.ks_apply_global_discount == 'after':
                if rec.ks_global_discount_type == 'percent':
                    rec.ks_amount_discount = (rec.amount_total * (rec.ks_global_discount_rate/100))
                    rec.amount_total = rec.amount_total - (rec.amount_total * (rec.ks_global_discount_rate/100))
                else:
                    rec.amount_total = rec.amount_total - ks_amount_discount
            if rec.ks_apply_global_discount == 'before':
                rec.amount_tax = total_tax
                rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.ks_amount_discount

    @api.constrains('ks_global_discount_rate')
    def ks_check_discount_value(self):
        if self.ks_global_discount_type == "percent":
            if self.ks_global_discount_rate > 100 or self.ks_global_discount_rate < 0:
                raise ValidationError('You cannot enter percentage value greater than 100.')
        else:
            if self.ks_global_discount_rate < 0 or self.ks_global_discount_rate > self.amount_untaxed:
                raise ValidationError(
                    'You cannot enter discount amount greater than actual cost or value lower than 0.')


class KsSaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        invoice = super(KsSaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if invoice:
            invoice['ks_global_discount_rate'] = order.ks_global_discount_rate
            invoice['ks_global_discount_type'] = order.ks_global_discount_type
            invoice['ks_apply_global_discount'] = order.ks_apply_global_discount
        return invoice
