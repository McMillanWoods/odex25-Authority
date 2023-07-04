# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import get_lang


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    state = fields.Selection(
        selection=[('draft', 'Draft'), ('direct manager', 'Direct Manager'),
                   ('send_budget', 'Send to Budget Confirmation'), ('wait_budget', 'Wait Budget'),
                   ('budget_approve', 'Budget Approved'),
                   ('cs_approve', 'Common Services Approval'),
                   ('general_supervisor', 'General Supervisor Approval'),
                   ('waiting', 'In Purchase'),
                   ('done', 'Done'), ('cancel', 'Cancel'), ('refuse', 'Refuse')], default="draft", tracking=True)
    requesting_administration = fields.Selection([
        ('planned for', 'Planned For'),
        ('emergency', 'Emergency')])
    planned_for = fields.Boolean()
    emergency = fields.Boolean()
    available = fields.Boolean()
    unavailable = fields.Boolean()
    specifications_conform = fields.Boolean(string="Technical specifications conform")
    specifications_not_conform = fields.Boolean(string="Technical specifications do not match")
    is_analytic = fields.Boolean("Use Analytic Account")
    type_id = fields.Many2one('purchase.requisition.type', string="Agreement Type")
    confirmation_ids = fields.One2many('budget.confirmation', 'request_id')
    custom_three_validation_steps = fields.Boolean("Special validation steps")

    def action_cs_approve(self):
        for request in self:
            request.write({'state': 'general_supervisor'})

    def action_general_supervisor_approve(self):
        for request in self:
            request.write({'state': 'waiting'})

    def action_confirm(self):
        if len(self.line_ids) == 0:
            raise ValidationError(_("Can't Confirm Request With No Item!"))
        if not self.department_id:
            raise ValidationError(_("Please Select department for employee"))
        else:
            self.write({
                'state': 'direct manager'
            })
            # Send Notifications

            subject = _('Purchase Request Confirmation') + ' - {}'.format(self.name)
            message = '{} '.format(self.name) + _('need your confirmation.') + '\n' + _('Create Date: ') + '{}'.format(
                self.create_date)
            group = 'purchase_requisition_custom.group_direct_manger'
            author_id = self.env.user.partner_id.id or None
            self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
                                                               group=group)
        if self.name == '/':
            self.name = self.env['ir.sequence'].next_by_code('stock.request.order') or '/'

    def approve_department(self):
        self.write({
            'state': 'send_budget'
        })
        # Send Notifications
        subject = _('Purchase Request Approve') + ' - {}'.format(self.name)
        message = '{} '.format(self.name) + _('need your approve.') + '\n' + _('Create Date: ') + '{}'.format(
            self.create_date)
        group = 'purchase_requisition_custom.group_department_approve'
        author_id = self.env.user.partner_id.id or None
        self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
                                                           group=group)

    def action_refuse(self):
        self.write({
            'state': 'refuse'
        })

    def action_refuse_department(self):
        self.write({
            'state': 'refuse'
        })

    def action_done(self):
        self.write({
            'state': 'done'
        })

    def action_budget(self):
        confirmation_lines = []
        amount = 0
        analytic_account = self.department_id.analytic_account_id
        for rec in self.line_ids:
            if not analytic_account:
                raise ValidationError(_('There is no analytic account for this purchase request'))
            if not rec.product_id:
                raise ValidationError(_('There is no product'))
            if not (rec.product_id.property_account_expense_id.id and
                    rec.product_id.property_account_expense_id.id or
                    rec.product_id.categ_id.property_account_expense_categ_id.id):
                raise ValidationError(_("This product has no expense account") + ': {}'.format(rec.product_id.name))
            budget_lines = analytic_account.crossovered_budget_line.filtered(
                lambda x:
                x.crossovered_budget_id.state == 'done' and
                fields.Date.from_string(x.date_from) <= fields.Date.from_string(
                    self.date) <= fields.Date.from_string(x.date_to))
            if budget_lines:
                remain = abs(budget_lines[0].remain)
                amount = amount + rec.sum_total
                new_remain = remain - amount
                confirmation_lines.append((0, 0, {
                    'amount': rec.sum_total,
                    'analytic_account_id': analytic_account.id,
                    'description': rec.product_id.name,
                    'budget_line_id': budget_lines[0].id,
                    'remain': new_remain + rec.sum_total,
                    'new_balance': new_remain,
                    'account_id': rec.product_id.property_account_expense_id.id and
                                  rec.product_id.property_account_expense_id.id or
                                  rec.product_id.categ_id.property_account_expense_categ_id.id
                }))
            else:
                raise ValidationError(
                    _(''' No budget for this service ''') + ': {} - {}'.format(rec.product_id.name,
                                                                               analytic_account.name))
                # Create budget.confirmation
        if confirmation_lines:
            data = {
                'name': self.name,
                'date': self.date,
                'beneficiary_id': self.partner_id.id,
                'department_id': self.department_id.id,
                'type': 'purchase.request',
                'ref': self.name,
                'description': self.purchase_purpose,
                'total_amount': amount,
                'lines_ids': confirmation_lines,
                'request_id': self.id,
                'planned_for': self.planned_for,
                'emergency': self.emergency,
                'available': self.available,
                'unavailable': self.unavailable,
                'specifications_conform': self.specifications_conform,
                'specifications_not_conform': self.specifications_not_conform,
            }
            budget_id = self.env['budget.confirmation'].create(data)
            subject = _('New Purchase Request')
            message = _(
                "New Budget Confirmation Has Been Created for Purchase Request %s to Beneficiary %s in total %s" % (
                    budget_id.name, budget_id.beneficiary_id.name, budget_id.total_amount))
            group = 'purchase.group_purchase_manager'
            author_id = self.env.user.partner_id.id or None
            self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id,
                                                               group=group)
            self.write({'state': 'wait_budget'})

    def create_requisition(self):
        if not self.employee_id.department_id:
            raise ValidationError(_("Choose A Department For this Employee!"))
        line_ids = []
        for line in self.line_ids:
            line_ids.append((0, 6, {
                'product_id': line.product_id.id,
                'department_id': line.request_id.department_id.id or False,
                'product_qty': line.qty,
                'name': line.name,
                'account_analytic_id': line.account_id.id,
            }))
        requisition_id = self.env['purchase.requisition'].sudo().create({
            'category_ids': self.product_category_ids.ids,
            'type_id': self.type_id.id,
            'department_id': self.employee_id.department_id.id,
            'type': self.type,
            'project_id': self.project_id.id,
            'project_stage_id': self.project_stage_id.id,
            'purpose': self.purchase_purpose,
            'request_id': self.id,
            'user_id': self.employee_id.user_id.id,
            'line_ids': line_ids
        })
        self.write({
            'purchase_create': True,
            'state': 'waiting'
        })

        return {
            'name': "Request for Quotation",
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.requisition',
            'view_mode': 'form',
            'res_id': requisition_id.id,
        }

    def action_cancel(self):
        self.write({
            'state': 'cancel'
        })

    def open_confirmation(self):
        formview_ref = self.env.ref('account_budget_custom.view_budget_confirmation_form', False)
        treeview_ref = self.env.ref('account_budget_custom.view_budget_confirmation_tree', False)
        return {
            'name': ("Budget  Confirmation"),
            'view_mode': 'tree, form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'budget.confirmation',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % self.confirmation_ids.ids,
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'),
                      (formview_ref and formview_ref.id or False, 'form')],
            'context': {'create': False}
        }


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    product_id = fields.Many2one('product.product', domain=lambda self: [('purchase_ok', '=', True)])
    name_text = fields.Char(string='Category')
    name_text1 = fields.Char(string='Specifications')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    sum_total = fields.Float()

    @api.onchange('qty', 'price_unit')
    def total_sum_lines(self):
        if self.price_unit and self.qty:
            self.sum_total = self.qty * self.price_unit

    # get price for product
    def _product_id_change(self):
        if not self.product_id:
            return

        product_lang = self.product_id.with_context(
            lang=get_lang(self.env, self.partner_id.lang).code,
            partner_id=self.partner_id.id,
            company_id=self.company_id.id,
        )
        self.name = self._get_product_purchase_description(product_lang)

    @api.constrains('qty')
    def qty_validation(self):
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError(_("Item Quantity MUST be at Least ONE!"))
