# -*- coding: utf-8 -*-

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def create(self, vals):
        vals.update({'flag': True})
        return super(AccountPayment, self).create(vals)


AccountPayment()
