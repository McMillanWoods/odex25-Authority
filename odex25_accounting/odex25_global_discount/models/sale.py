# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('discount_amount', 'discount_method', 'discount_type')
    def _calculate_discount(self):
        res = 0.0
        discount = 0.0
        for self_obj in self:
            if self_obj.discount_method == 'fix':
                discount = self_obj.discount_amount
                res = discount
            elif self_obj.discount_method == 'per':
                discount = self_obj.amount_untaxed * (self_obj.discount_amount / 100)
                res = discount
            else:
                res = discount
        return res

    @api.depends('order_line', 'order_line.price_total', 'order_line.price_subtotal', \
                 'order_line.product_uom_qty', 'discount_amount', \
                 'discount_method', 'discount_type', 'order_line.discount_amount', \
                 'order_line.discount_method', 'order_line.discount_amt')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """

        tax_discount_policy = self.env['ir.config_parameter'].sudo().get_param(
            'odex25_global_discount.tax_discount_policy')
        cur_obj = self.env['res.currency']
        for order in self:
            applied_discount = line_discount = sums  = amount_untaxed = amount_tax  = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                applied_discount += line.discount_amt

                if line.discount_method == 'fix':
                    line_discount += line.discount_amount
                elif line.discount_method == 'per':
                    # line_discount += line.price_unit * (line.discount_amount/ 100)
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
                            order_discount = (amount_untaxed + amount_tax) * (order.discount_amount / 100)
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
                            if line.discount_method == 'fix' and line.tax_id.price_include == True:
                                price_amount = amount_untaxed - line.discount_amount
                                taxes = line.tax_id.compute_all(price_amount, line.order_id.currency_id, 1,
                                                                product=line.product_id,
                                                                partner=line.order_id.partner_shipping_id)
                                sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            elif line.discount_method == 'per' and line.tax_id.price_include == True:
                                price_amount = line.price_subtotal - (
                                        (line.discount_amount * line.price_subtotal) / 100.0)
                                taxes = line.tax_id.compute_all(price_amount, line.order_id.currency_id, 1,
                                                                product=line.product_id,
                                                                partner=line.order_id.partner_shipping_id)
                                sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            elif line.discount_method == 'fix' and not line.tax_id.price_include == True:
                                sums = amount_tax
                            elif line.discount_method == 'per' and not line.tax_id.price_include == True:
                                sums = amount_tax
                            else:
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
                                    if line.tax_id:
                                        final_discount = 0.0
                                        try:
                                            final_discount = ((order.discount_amount * line.price_subtotal) / 100.0)
                                        except ZeroDivisionError:
                                            pass
                                        discount = line.price_subtotal - final_discount
                                        taxes = line.tax_id.compute_all(discount, \
                                                                        order.currency_id, 1.0, product=line.product_id, \
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
                                    if line.tax_id:
                                        final_discount = 0.0
                                        try:
                                            final_discount = (
                                                    (order.discount_amount * line.price_subtotal) / amount_untaxed)
                                        except ZeroDivisionError:
                                            pass
                                        discount = line.price_subtotal - final_discount

                                        taxes = line.tax_id.compute_all(discount, \
                                                                        order.currency_id, 1.0, product=line.product_id, \
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

    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Monetary(compute='_amount_all', string='- Discount', digits='Discount', store=True,
                                   readonly=True)
    discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')], string='Discount Applies to',
                                     default='global')
    discount_amt_line = fields.Float(compute='_amount_all', string='- Line Discount', digits='Line Discount',
                                     store=True, readonly=True)

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({'discount_method': self.discount_method,
                    'discount_amount': self.discount_amount,
                    'discount_amt': self.discount_amt,
                    'discount_type': self.discount_type,
                    'discount_amt_line': self.discount_amt_line,
                    'is_line': True, })
        return res


SaleOrder()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_method', 'discount_amount')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        tax_discount_policy = self.env['ir.config_parameter'].sudo().get_param(
            'odex25_global_discount.tax_discount_policy')
        for line in self:
            if tax_discount_policy:
                if tax_discount_policy == 'untax':
                    if line.discount_type == 'line':
                        if line.discount_method == 'fix' and line.tax_id.price_include == True:
                            price = (line.price_unit * line.product_uom_qty) - line.discount
                            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1,
                                                            product=line.product_id,
                                                            partner=line.order_id.partner_shipping_id)
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'],
                                'price_subtotal': taxes['total_excluded'],
                                'discount_amt': line.discount_amount,
                            })
                        elif line.discount_method == 'fix' and not line.tax_id.price_include == True:
                            price = (line.price_unit * line.product_uom_qty) - line.discount_amount
                            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1,
                                                            product=line.product_id,
                                                            partner=line.order_id.partner_shipping_id)
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + line.discount_amount,
                                'price_subtotal': taxes['total_excluded'] + line.discount_amount,
                                'discount_amt': line.discount_amount,
                            })

                        elif line.discount_method == 'per' and not line.tax_id.price_include == True:
                            price = (line.price_unit * line.product_uom_qty) * (
                                    1 - (line.discount_amount or 0.0) / 100.0)
                            price_x = ((line.price_unit * line.product_uom_qty) - (
                                    line.price_unit * line.product_uom_qty) * (
                                               1 - (line.discount_amount or 0.0) / 100.0))
                            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1,
                                                            product=line.product_id,
                                                            partner=line.order_id.partner_shipping_id)
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + price_x,
                                'price_subtotal': taxes['total_excluded'] + price_x,
                                'discount_amt': price_x,
                            })
                        elif line.discount_method == 'per' and line.tax_id.price_include == True:
                            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1,
                                                            product=line.product_id,
                                                            partner=line.order_id.partner_shipping_id)
                            price_x = ((taxes['total_excluded'] * line.product_uom_qty) - (
                                    taxes['total_excluded'] * line.product_uom_qty) * (
                                               1 - (line.discount_amount or 0.0) / 100.0))
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'],
                                'price_subtotal': taxes['total_excluded'],
                                'discount_amt': price_x,
                            })
                        else:
                            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                            product=line.product_id,
                                                            partner=line.order_id.partner_shipping_id)
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'],
                                'price_subtotal': taxes['total_excluded'],
                            })
                    else:
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                        taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                        product=line.product_id,
                                                        partner=line.order_id.partner_shipping_id)

                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })

                elif tax_discount_policy == 'tax':
                    if line.discount_type == 'line':
                        price_x = 0.0
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                        taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                        product=line.product_id,
                                                        partner=line.order_id.partner_shipping_id)

                        if line.discount_method == 'fix':
                            price_x = (taxes['total_included']) - (taxes['total_included'] - line.discount_amount)
                        elif line.discount_method == 'per':
                            price_x = (taxes['total_included']) - (
                                    taxes['total_included'] * (1 - (line.discount_amount or 0.0) / 100.0))
                        else:
                            price_x = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                            'discount_amt': price_x,
                        })
                    else:
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                        taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                        product=line.product_id,
                                                        partner=line.order_id.partner_shipping_id)
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
                else:
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                    product=line.product_id, partner=line.order_id.partner_shipping_id)

                    line.update({
                        'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_shipping_id)

                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

    is_apply_on_discount_amount = fields.Boolean("Tax Apply After Discount")
    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_type = fields.Selection(related='order_id.discount_type', string="Discount Applies to")
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float('Discount Final Amount')

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res.update({'discount': self.discount,
                    'discount_method': self.discount_method,
                    'discount_amount': self.discount_amount,
                    'discount_amt': self.discount_amt, })
        return res


SaleOrderLine()
