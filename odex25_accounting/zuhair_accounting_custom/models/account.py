from odoo import models, fields


class Account(models.Model):
    _inherit = 'account.account'

    is_other_cash_flow = fields.Boolean(string="Other Cash Flow", )
