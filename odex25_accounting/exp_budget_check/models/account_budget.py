from odoo import api, fields, models, _


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    reserve = fields.Float(string='Reserve Amount')
    confirm = fields.Float(string='Confirm Amount')

    def _compute_operations_amount(self):
        if not self.ids: return
        for line in self:
            pull_out = provide = budget_confirm_amount = 0.0
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get(
                'wizard_date_from') or line.date_from

            if line.analytic_account_id.id:
                if 'reserved' not in self.env.context:
                    self.env.cr.execute("""
                           SELECT SUM(amount)
                           FROM budget_operations
                           WHERE from_budget_line_id=%s
                               AND (date between %s AND %s)
                               AND state='confirmed'""",
                                        (line.id, date_from, date_to,))
                    pull_out = self.env.cr.fetchone()[0] or 0.0

                if 'reserved' in self.env.context:
                    self.env.cr.execute("""
                           SELECT SUM(amount)
                           FROM budget_operations
                           WHERE from_budget_line_id=%s
                               AND (date between %s AND %s)
                               AND state='confirmed' 
                               AND from_reserved=%s""",
                                        (line.id, date_from, date_to, self.env.context['reserved']))
                    pull_out = self.env.cr.fetchone()[0] or 0.0

                self.env.cr.execute("""
                       SELECT SUM(amount)
                       FROM budget_operations
                       WHERE to_budget_line_id=%s
                           AND (date between %s AND %s)
                           AND state='confirmed'""",
                                    (line.id, date_from, date_to,))
                provide = self.env.cr.fetchone()[0] or 0.0

                self.env.cr.execute("""
                       SELECT SUM(amount)
                       FROM budget_confirmation_line
                       WHERE budget_line_id=%s
                           AND (date between %s AND %s)
                           AND state='done'""",
                                    (line.id, date_from, date_to,))
                budget_confirm_amount = self.env.cr.fetchone()[0] or 0.0

            line.pull_out = pull_out
            line.provide = provide
            line.budget_confirm_amount = budget_confirm_amount


            line.remain = line.planned_amount + provide - pull_out - \
                          line.practical_amount - line.reserved_amount  + line.reserve
