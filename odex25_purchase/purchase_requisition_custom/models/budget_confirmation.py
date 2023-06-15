from odoo import api, fields, models, _


class BudgetConfirmationCustom(models.Model):
    _inherit = 'budget.confirmation'

    type = fields.Selection(
        selection_add=[('purchase.order', 'Purchase Requisition'), ('purchase.request', 'Purchase Request')])
    po_id = fields.Many2one('purchase.order')
    request_id = fields.Many2one('purchase.request')
    confirm_po = fields.Boolean()
    confirm_invoice = fields.Boolean()

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
            for rec in budget_lines:
                if self.po_id and self.type == 'purchase.order':
                # Update reserve of budget_lines
                    self.get_confirm_reserve(rec)
                    if self.po_id and self.po_id.requisition_id:
                        self.po_id.write({'state': 'to approve'})  # draft
                        self.po_id.requisition_id.write({'state': 'checked'})
                    elif self.po_id:
                        if self.po_id.email_to_vendor:
                            self.po_id.write({'state': 'sent'})
                        else:
                            self.po_id.write({'state': 'draft'})
                    if self.po_id.request_id:
                        lines = self.po_id.request_id.confirmation_ids
                        for r in lines:
                            r.confirm_po = True
                        self.get_initial_reserve(rec)

                if self.request_id and self.type == 'purchase.request':
                    self.get_initial_reserve(rec)
                    self.request_id.write({'state': 'budget_approve'})

    def get_initial_reserve(self,rec):
        amount = sum(rec.budget_confirm_line_ids.filtered(lambda r: not r.confirmation_id.confirm_po and r.confirmation_id.state=='done'
                                                                    and r.confirmation_id.type == 'purchase.request').mapped('amount'))
        rec.write({'initial_reserve': amount})


    def get_confirm_reserve(self,rec):
        amount = sum(rec.budget_confirm_line_ids.filtered(lambda r: not r.confirmation_id.confirm_invoice and r.confirmation_id.state=='done'
                                                                    and r.confirmation_id.type == 'purchase.order').mapped('amount'))
        rec.write({'reserve': amount})
class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"


    budget_confirm_line_ids = fields.One2many('budget.confirmation.line','budget_line_id','Confirmation')
