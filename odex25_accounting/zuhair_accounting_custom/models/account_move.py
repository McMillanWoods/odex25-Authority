from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    execution_guarantee_amount = fields.Float(string="Execution Guarantee Amount", required=False, )
    aging_date = fields.Date(string="Aging Date", required=False, )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_execution_guarantee = fields.Boolean(string="Execution Guarantee", required=False, )
