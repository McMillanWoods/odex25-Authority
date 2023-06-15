from odoo import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    government_type = fields.Selection(string="Governmental Type",
                                       selection=[('gov', 'Governmental'), ('not_gov', 'Non-Governmental'), ],
                                       required=False, )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    before_tax_amount = fields.Float(string="Before Tax amount", compute="_get_before_tax")

    # entry_tax_amount = fields.Float(string="Before Tax amount", compute="_get_entry_tax")

    def _get_before_tax(self):
        for rec in self:
            rec.before_tax_amount = 0.0
            bank_tax = rec.tax_ids.filtered(lambda x: x.name == "ضرائب العمولات البنكية")
            if bank_tax:
                print(bank_tax, 'bank_tax')
                rec.before_tax_amount = rec.debit

        # if rec.statement_id:
        # account = rec.statement_id.journal_id.default_account_id
        # line = rec.move_id.line_ids.filtered(lambda l: l.account_id.id == account.id)
        # if line:
        #     rec.before_tax_amount = rec.balance
