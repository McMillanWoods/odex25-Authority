# -*- coding: utf-8 -*-
from odoo import fields, models, _


class BudgetConfirmationCustom(models.Model):
    _inherit = 'budget.confirmation'

    type = fields.Selection(
        selection_add=[('purchase.order', 'Purchase Requisition'), ('purchase.request', 'Purchase Request')])
    po_id = fields.Many2one('purchase.order')
    request_id = fields.Many2one('purchase.request')
    planned_for = fields.Boolean(string="Planned For")
    emergency = fields.Boolean(string="Emergency")
    available = fields.Boolean(string="Available")
    unavailable = fields.Boolean(string="Unavailable")
    specifications_conform = fields.Boolean(string="Technical specifications conform")
    specifications_not_conform = fields.Boolean(string="Technical specifications do not match")

    def cancel(self):
        super(BudgetConfirmationCustom, self).cancel()
        if self.po_id and self.type == 'purchase.order':
            self.po_id.write({'state': 'budget_rejected'})
            body = _(
                "Purchase Order %s is Rejected By : %s  With Reject Reason : %s" % (
                    str(self.name), str(self.env.user.name), str(self.reject_reason)))
            # Send Notifications
            subject = _('Reject Purchase Order')
            author_id = self.env.user.partner_id.id or None
            self.create_uid.partner_id.send_notification_message(subject=subject, body=body, author_id=author_id)
            self.po_id.message_post(body=body)

    def done(self):
        super(BudgetConfirmationCustom, self).done()
        for line in self.lines_ids:
            budget_post = self.env['account.budget.post'].search([]).filtered(
                lambda x: line.account_id in x.account_ids)
            analytic_account_id = line.analytic_account_id
            budget_lines = analytic_account_id.crossovered_budget_line.filtered(
                lambda x: x.general_budget_id in budget_post and
                          x.crossovered_budget_id.state == 'done' and
                          x.date_from <= self.date <= x.date_to)
            if self.po_id and self.type == 'purchase.order':
            # Update reserve of budget_lines
                amount = budget_lines.reserve
                amount += line.amount
                budget_lines.write({'reserve': amount})

                if self.po_id and self.po_id.requisition_id:
                    self.po_id.write({'state': 'to approve'})  # draft
                    self.po_id.requisition_id.write({'state': 'checked'})
                elif self.po_id:
                    if self.po_id.email_to_vendor:
                        self.po_id.write({'state': 'sent'})
                    else:
                        self.po_id.write({'state': 'draft'})
            if self.request_id and self.type == 'purchase.request':
                amount = budget_lines.initial_reserve
                amount += line.amount
                budget_lines.write({'initial_reserve': amount})
                if self.request_id.custom_three_validation_steps:
                    self.request_id.write({'state': 'cs_approve'})
                else:
                    self.request_id.write({'state': 'budget_approve'})
