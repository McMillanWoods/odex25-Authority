# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class AccountExecutionGuaranteeWizard(models.TransientModel):
    _name = "account.execution.guarantee.wizard"
    _description = 'Account Execution Guarantee Wizard'

    name = fields.Char(string="Name", default='Execution Guarantee')
    percentage = fields.Float(string="Percentage", default=1.0)

    account_id = fields.Many2one(comodel_name="account.account", string="Discount Account", required=False, )

    def create_execution_guarantee_line(self):
        move = self.env['account.move'].browse(self._context.get('active_id'))
        move.invoice_line_ids.filtered(lambda r: r.is_execution_guarantee).unlink()

        account = self.account_id
        if move and account:
            vls = {
                'name': self.name,
                'account_id': account.id,
                'is_execution_guarantee': True,
                'quantity': 1,
                'price_unit': -1 * (move.amount_untaxed * (self.percentage / 100)),
            }
            move.write({
                'execution_guarantee_amount': move.amount_untaxed * (self.percentage / 100),
                'invoice_line_ids': [(0, 0, vls)]
            })
