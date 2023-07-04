# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    quote_number = fields.Char(
        string='Quotation Reference',
        readonly=True,
        copy=False,
        help="When you confirm quotation new sequence will generate for "
             "approved purchase order,this field keep/store old quotation number "
             "for future reference."
    )

    def button_approve(self, force=False):
        super(PurchaseOrder, self).button_approve(force=False)
        for order in self:
            if not order.quote_number:
                order.write({
                    'quote_number': order.name,
                    'name': self.env['ir.sequence'].next_by_code(
                        'purchase.order.new_seq')
                })
