from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class AccountMove(models.Model):
    _inherit = 'account.move'

#     def button_cancel(self):
#         res = super(AccountMove, self).button_cancel()
#         date = fields.Date.from_string(self.date)
#         confirm_budget = self.env['budget.confirmation'].search([('po_id', '=', self.purchase_id.id)])
#         if confirm_budget:
#             for line in self.invoice_line_ids:
#                 analytic_account_id = line.analytic_account_id
#                 budget_post = self.env['account.budget.post'].search([]).filtered(
#                     lambda x: line.account_id in x.account_ids)
#                 budget_lines = analytic_account_id.crossovered_budget_line.filtered(
#                     lambda x: x.general_budget_id in budget_post and
#                               x.crossovered_budget_id.state == 'done' and
#                               fields.Date.from_string(x.date_from) <= date <= fields.Date.from_string(x.date_to))
#                 amount = budget_lines.reserve
#                 amount -= (line.price_subtotal + line.price_tax)
#                 budget_lines.write({'reserve': amount})

#             return res


#     def action_post(self):
#         res = super(AccountMove, self).action_post()
#         confirm_budget = self.env['budget.confirmation'].search([('po_id', '=', self.purchase_id.id)])
#         if confirm_budget:
#             for line in self.invoice_line_ids:
#                 analytic_account_id = line.analytic_account_id
#                 budget_post = self.env['account.budget.post'].search([]).filtered(
#                     lambda x: line.account_id in x.account_ids)
#                 budget_lines = analytic_account_id.crossovered_budget_line.filtered(
#                     lambda x: x.general_budget_id in budget_post and
#                               x.crossovered_budget_id.state == 'done' and
#                               x.date_from <= self.invoice_date <= x.date_to)
#                 budget_lines.write({'reserve': abs((line.price_subtotal + line.price_tax) - budget_lines.reserve)})

#             return res

# def button_draft(self):
#     res = super(AccountMove, self).button_draft()
#     if self.is_check:
#         date = fields.Date.from_string(self.date)
#         for line in self.invoice_line_ids:
#             analytic_account_id = line.analytic_account_id
#             budget_post = self.env['account.budget.post'].search([]).filtered(
#                 lambda x: line.account_id in x.account_ids)
#             budget_lines = analytic_account_id.crossovered_budget_line.filtered(
#                 lambda x: x.general_budget_id in budget_post and
#                           x.crossovered_budget_id.state == 'done' and
#                           fields.Date.from_string(x.date_from) <= date <= fields.Date.from_string(x.date_to))
#             amount = budget_lines.confirm
#             amount -= (line.price_subtotal + line.price_tax)
#             budget_lines.write({'confirm': amount})
#     return res


# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'

#     price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

#     @api.depends('quantity', 'price_unit', 'tax_ids')
#     def _compute_amount(self):
#         for line in self:
#             taxes = line.tax_ids.compute_all(line.price_unit, line.move_id.currency_id, line.quantity,
#                                              product=line.product_id, partner=line.move_id.partner_id)
#             line.update({
#                 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#             })
