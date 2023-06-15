# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    discount_account = fields.Boolean('Discount Account')


AccountAccount()
