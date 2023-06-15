# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line', 'order_line.price_total', 'order_line.price_subtotal', \
                 'order_line.product_qty', 'discount_amount', \
                 'discount_method', 'discount_type', 'order_line.discount_amount', \
                 'order_line.discount_method')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        tax_discount_policy = self.env['ir.config_parameter'].sudo().get_param(
            'odex25_global_discount.tax_discount_policy')
        for order in self:
            applied_discount = line_discount = sums = amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                applied_discount += line.discount_amt
                if line.discount_method == 'fix':
                    line_discount += line.discount_amount
                elif line.discount_method == 'per':
                    line_discount += (line.price_subtotal+line.price_tax) * (line.discount_amount / 100)
            if tax_discount_policy:
                if tax_discount_policy == 'tax':
                    if order.discount_type == 'line':
                        order.discount_amt = 0.00
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax - line_discount,
                            'discount_amt_line': line_discount,
                        })
                    elif order.discount_type == 'global':
                        order.discount_amt_line = 0.00
                        if order.discount_method == 'per':
                            order_discount = (amount_untaxed+amount_tax) * (order.discount_amount / 100)
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discount_amt': order_discount,
                            })
                        elif order.discount_method == 'fix':
                            order_discount = order.discount_amount
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discount_amt': order_discount,
                            })
                        else:
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax,
                            })
                    else:
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax,
                        })
                elif tax_discount_policy == 'untax':
                    if order.discount_type == 'line':
                        order.discount_amt = 0.00
                        for line in order.order_line:
                            if line.discount_method == 'fix' and line.taxes_id.price_include == True:
                                price_amount = amount_untaxed - line.discount_amount
                                taxes = line.taxes_id.compute_all(price_amount, line.order_id.currency_id, 1,
                                                                  product=line.product_id, partner=order.partner_id)
                                sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            elif line.discount_method == 'per' and line.taxes_id.price_include == True:
                                price_amount = line.price_subtotal - (
                                            (line.discount_amount * line.price_subtotal) / 100.0)
                                taxes = line.taxes_id.compute_all(price_amount, line.order_id.currency_id, 1,
                                                                  product=line.product_id, partner=order.partner_id)
                                sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            elif line.discount_method == 'fix' and not line.taxes_id.price_include == True:
                                sums = amount_tax
                            elif line.discount_method == 'per' and not line.taxes_id.price_include == True:
                                sums = amount_tax
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': sums,
                            'amount_total': amount_untaxed + sums - applied_discount,
                            'discount_amt_line': applied_discount,
                        })
                    elif order.discount_type == 'global':
                        order.discount_amt_line = 0.00
                        if order.discount_method == 'per':
                            order_discount = amount_untaxed * (order.discount_amount / 100)
                            if order.order_line:
                                for line in order.order_line:
                                    if line.taxes_id:
                                        final_discount = 0.0
                                        try:
                                            final_discount = ((order.discount_amount * line.price_subtotal) / 100.0)
                                        except ZeroDivisionError:
                                            pass
                                        discount = line.price_subtotal - final_discount
                                        taxes = line.taxes_id.compute_all(discount, \
                                                                          order.currency_id, 1.0,
                                                                          product=line.product_id, \
                                                                          partner=order.partner_id)
                                        sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': sums,
                                'amount_total': amount_untaxed + sums - order_discount,
                                'discount_amt': order_discount,
                            })
                        elif order.discount_method == 'fix':
                            order_discount = order.discount_amount
                            if order.order_line:
                                for line in order.order_line:
                                    if line.taxes_id:
                                        final_discount = 0.0
                                        try:
                                            final_discount = (
                                                        (order.discount_amount * line.price_subtotal) / amount_untaxed)
                                        except ZeroDivisionError:
                                            pass
                                        discount = line.price_subtotal - final_discount
                                        taxes = line.taxes_id.compute_all(discount, \
                                                                          order.currency_id, 1.0,
                                                                          product=line.product_id, \
                                                                          partner=order.partner_id)
                                        sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': sums,
                                'amount_total': amount_untaxed + sums - order_discount,
                                'discount_amt': order_discount,
                            })
                        else:
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax,
                            })
                    else:
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax,
                        })
                else:
                    order.update({
                        'amount_untaxed': amount_untaxed,
                        'amount_tax': amount_tax,
                        'amount_total': amount_untaxed + amount_tax,
                    })
            else:
                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': amount_untaxed + amount_tax,
                })

    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res.update({
            'discount_method': self.discount_method,
            'discount_amt': self.discount_amt,
            'discount_amount': self.discount_amount,
            'discount_type': self.discount_type,
            'discount_amt_line': self.discount_amt_line,
        })
        return res

    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method', default='fix')
    discount_amount = fields.Float('Discount Amount', default=0.0)
    discount_amt = fields.Monetary(compute='_amount_all', store=True, string='- Discount', readonly=True)
    discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')], string='Discount Applies to',
                                     default='global')
    discount_amt_line = fields.Float(compute='_amount_all', string='- Line Discount', digits='Line Discount',
                                     store=True, readonly=True)


PurchaseOrder()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    discount_method = fields.Selection(
        [('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_type = fields.Selection(related='order_id.discount_type', string="Discount Applies to")
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float('Discount Final Amount')

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount_method', 'discount_amount', 'discount_type')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            tax_discount_policy = self.env['ir.config_parameter'].sudo().get_param(
                'odex25_global_discount.tax_discount_policy')
            if tax_discount_policy:
                if tax_discount_policy == 'untax':
                    if line.discount_type == 'line':
                        if line.discount_method == 'fix' and not line.taxes_id.price_include == True:
                            price = (vals['price_unit'] * vals['product_qty']) - line.discount_amount
                            taxes = line.taxes_id.compute_all(price, vals['currency_id'], 1, vals['product'],
                                                              vals['partner'])
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + line.discount_amount,
                                'price_subtotal': taxes['total_excluded'] + line.discount_amount,
                                'discount_amt': line.discount_amount,
                            })
                        elif line.discount_method == 'fix' and line.taxes_id.price_include == True:
                            price = (vals['price_unit'] * vals['product_qty'])
                            taxes = line.taxes_id.compute_all(price, vals['currency_id'], 1, vals['product'],
                                                              vals['partner'])
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'],
                                'price_subtotal': taxes['total_excluded'],
                                'discount_amt': line.discount_amount,
                            })
                        elif line.discount_method == 'per' and not line.taxes_id.price_include == True:
                            price = (vals['price_unit'] * vals['product_qty']) * (
                                        1 - (line.discount_amount or 0.0) / 100.0)
                            price_x = ((vals['price_unit'] * vals['product_qty']) - (
                                        (vals['price_unit'] * vals['product_qty']) * (
                                            1 - (line.discount_amount or 0.0) / 100.0)))
                            taxes = line.taxes_id.compute_all(price, vals['currency_id'], 1, vals['product'],
                                                              vals['partner'])
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + price_x,
                                'price_subtotal': taxes['total_excluded'] + price_x,
                                'discount_amt': price_x,
                            })
                        elif line.discount_method == 'per' and line.taxes_id.price_include == True:
                            price = vals['price_unit']
                            taxes = line.taxes_id.compute_all(price, vals['currency_id'], 1, vals['product'],
                                                              vals['partner'])
                            price_x = ((taxes['total_excluded'] * vals['product_qty']) - (
                                        (taxes['total_excluded'] * vals['product_qty']) * (
                                            1 - (line.discount_amount or 0.0) / 100.0)))

                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'],
                                'price_subtotal': taxes['total_excluded'],
                                'discount_amt': price_x,
                            })
                        else:
                            taxes = line.taxes_id.compute_all(vals['price_unit'], vals['currency_id'],
                                                              vals['product_qty'], vals['product'], vals['partner'])
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'],
                                'price_subtotal': taxes['total_excluded'],
                            })
                    else:
                        taxes = line.taxes_id.compute_all(vals['price_unit'], vals['currency_id'], vals['product_qty'],
                                                          vals['product'], vals['partner'])
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
                elif tax_discount_policy == 'tax':
                    price_x = 0.0
                    if line.discount_type == 'line':
                        taxes = line.taxes_id.compute_all(vals['price_unit'], vals['currency_id'], vals['product_qty'],
                                                          vals['product'], vals['partner'])
                        if line.discount_method == 'fix':
                            price_x = (taxes['total_included']) - (taxes['total_included'] - line.discount_amount)
                        elif line.discount_method == 'per':
                            price_x = (taxes['total_included']) - (
                                        taxes['total_included'] * (1 - (line.discount_amount or 0.0) / 100.0))

                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                            'discount_amt': price_x,
                        })
                    else:
                        taxes = line.taxes_id.compute_all(vals['price_unit'], vals['currency_id'], vals['product_qty'],
                                                          vals['product'], vals['partner'])
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
                else:
                    taxes = line.taxes_id.compute_all(vals['price_unit'], vals['currency_id'], vals['product_qty'],
                                                      vals['product'], vals['partner'])
                    line.update({
                        'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })
            else:
                taxes = line.taxes_id.compute_all(vals['price_unit'], vals['currency_id'], vals['product_qty'],
                                                  vals['product'], vals['partner'])
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)

        res.update({'discount_method': self.discount_method, 'discount_amount': self.discount_amount})
        return res


PurchaseOrderLine()
