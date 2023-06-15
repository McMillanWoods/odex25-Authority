# -*- coding: utf-8 -*-
##############################################################################
#
#    Expert Co. Ltd.
#    Copyright (C) 2018 (<http://www.exp-sa.com/>).
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    budget_line_id = fields.Many2one('crossovered.budget.lines')

    @api.multi
    def check_budget(self):
        """
        Check the available budget for given account and
        analytic amount in defined period of time
        :return:
        """
        if self.account_analytic_id and not self.purchase_line_id:
            date = fields.Date.from_string(self.invoice_id.date_invoice)
            budget_post = self.env['account.budget.post'].search([]).filtered(
                lambda x: self.account_id in x.account_ids)
            budget_lines = self.account_analytic_id.crossovered_budget_line.filtered(
                lambda x: x.general_budget_id in budget_post and
                          x.crossovered_budget_id.state == 'done' and
                          fields.Date.from_string(x.date_from) <= date and
                          fields.Date.from_string(x.date_to) >= date)

            if budget_lines:
                remain = budget_lines[0].remain
                amount = self.price_unit * self.quantity * (1 - self.discount / 100)
                if remain >= amount:
                    self.budget_line_id = budget_lines[0]
                else:
                    raise ValidationError(_('''No enough budget for account (%s) and cost center (%s)''') %
                                          (self.account_id.name, self.account_analytic_id.name))
            else:
                raise ValidationError(_('''No budget for (%s) and cost center (%s)''') %
                                      (self.account_id.name, self.account_analytic_id.name))


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    confirm_amount = fields.Float(string='confirmation amount', compute='_compute_confirm_amount')

    @api.multi
    def _compute_confirm_amount(self):
        if not self.ids: return
        for line in self:
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            if line.analytic_account_id.id:
                self.env.cr.execute("""
                                    SELECT SUM(price_unit*quantity*(1-discount/100))
                                    FROM account_invoice_line INNER JOIN account_invoice inv ON
                                         inv.id=invoice_id
                                    WHERE budget_line_id=%s AND purchase_line_id IS NULL
                                        AND (date_invoice between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                                        AND inv.state NOT IN ('draft','open','paid','cancel')""",
                                    (line.id, date_from, date_to,))
                inv_amount = self.env.cr.fetchone()[0] or 0.0
                self.env.cr.execute("""
                                    SELECT SUM(amount)
                                    FROM (
                                        SELECT distinct(prl.id),amount
                                        FROM purchase_requisition_line prl INNER JOIN purchase_requisition pr ON
                                             pr.id=prl.requisition_id INNER JOIN purchase_order po ON 
                                             pr.id=po.requisition_id LEFT OUTER JOIN account_invoice inv ON
                                             po.name=inv.origin
                                        WHERE budget_line_id=%s AND chosen=True AND inv.move_id IS NULL
                                            AND (ordering_date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                                            AND pr.state NOT IN ('draft','in_progress','purchase_manager','cancel')) amounts""",
                                    (line.id, date_from, date_to,))
                po_amount = self.env.cr.fetchone()[0] or 0.0
                line.confirm_amount = inv_amount + po_amount

    @api.multi
    def _compute_operations_amount(self):
        super(CrossoveredBudgetLines, self)._compute_operations_amount()
        for line in self:
            line.remain = line.planned_amount + line.provide - line.pull_out - \
                        line.practical_amount - line.reserved_amount - line.confirm_amount
