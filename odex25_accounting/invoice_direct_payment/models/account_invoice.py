# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from lxml import etree
import json

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    number = fields.Char(
        store=True, readonly=True, copy=False
    )
    payment_journal_id = fields.Many2one(
        'account.journal', string='Payment Method', readonly=True,states={'draft': [('readonly', False)]},domain="[('type', 'in', ['cash', 'bank'])]"
    )
    pay_now = fields.Selection(
        [('pay_now', 'Pay Directly'), ('pay_later', 'Pay Later')], 'Payment',
        index=True, readonly=True, states={'draft': [('readonly', False)]}, default='pay_now'
    )
    employee_id = fields.Many2one('hr.employee', default=lambda item: item.get_emp_id())
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', readonly=True)
    job_id = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True)
    bank_account_id = fields.Many2one('res.partner.bank', related='employee_id.bank_account_id', readonly=True)
    bank_code = fields.Char(related='employee_id.bank_code', readonly=True)
    mobile_phone = fields.Char(related='employee_id.mobile_phone', readonly=True)
    tracker_ids = fields.One2many('tracker', 'invoice_id')
    request = fields.Boolean()
    state = fields.Selection([
            ('draft', 'Draft'), ('direct', 'Direct Manager'), ('department_manager', 'Department Manager'),
            ('accountant', 'Accountant'), ('qc_approve', 'QC Approve'), ('financial_manager', 'Financial Manager'),
            ('open', 'Open'), ('paid', 'Paid'), ('cancel', 'Cancelled')],
        string='Status', index=True, readonly=True, default='draft', track_visibility='onchange', copy=False)
    account_analytic_id = fields.Many2one('account.analytic.account', related='invoice_line_ids.account_analytic_id',
                                          string='Cost Center', store=False, readonly=True)
    from_po = fields.Boolean(compute="_compute_from_po", string='This invoice Generated From Purchase')
    readonly = fields.Boolean(compute="compute_readonly")

    @api.multi
    def compute_readonly(self):
        """
        use this compute field to close some filed in view from all sers exept account user and manager
        """
        for rec in self:
            rec.readonly = False
            user = rec.user_has_groups(groups='account.group_account_user')
            manager = rec.user_has_groups(groups='account.group_account_manager')
            if not user and not manager:
                rec.readonly = True

    @api.depends('invoice_line_ids')
    def _compute_from_po(self):
        self.from_po = False
        purchase_ids = self.invoice_line_ids.mapped('purchase_id')
        if purchase_ids:
            self.from_po = True

    def check_line_account(self):
        for line in self.invoice_line_ids:
            if not line.account_id:
                raise ValidationError(_('Kindly Enter Account in line %s') % (line.name))

    @api.multi
    def get_emp_id(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid), ('state', '=', 'open')], limit=1)
        return employee_id and employee_id.id or False

    @api.onchange('employee_id')
    def onchange_employee(self):
        domain = {}
        self.partner_id = self.employee_id.sudo().address_home_id.id or self.sudo().employee_id.user_id.partner_id
        employee_ids = self.env['hr.employee'].sudo().search([('parent_id', 'child_of', self.employee_id.id)])
        users = employee_ids.mapped('user_id')
        domain['user_id'] = [('id', 'in', users.ids)]
        return {'domain': domain}

    def act_submit(self):
        self.tracker_ids.create({'invoice_id':self.id, 'state':self.state})
        if not self.number:
            self.number = self.env['ir.sequence'].with_context(ir_sequence_date =self.date_invoice).next_by_code('request.seq')
        self.state = 'direct'

    def act_direct(self):
        self.tracker_ids.create({'invoice_id':self.id, 'state':self.state})
        self.state = 'department_manager'

    def act_department_manager(self):
        self.tracker_ids.create({'invoice_id':self.id, 'state':self.state})
        self.state = 'accountant'

    def act_accountant(self):
        self.check_line_account()
        self.tracker_ids.create({'invoice_id':self.id, 'state':self.state})
        self.state = 'qc_approve'

    def act_qc_approve(self):
        self.tracker_ids.create({'invoice_id':self.id, 'state':self.state})
        self.state = 'financial_manager'

    def action_invoice_open(self):
        self.check_line_account()
        if self.pay_now == 'pay_now' and self.type == 'in_invoice':
            dict = {
                'invoice_ids': [(4, self.id, None)],
                'journal_id': self.payment_journal_id.id,
                'partner_id': self.partner_id.id,
                'partner_type': 'supplier',
                'payment_type': 'outbound',
                'amount': self.amount_total,
                'description': self.comment,
                'communication': self.number,
                'currency_id': self.currency_id.id,
                'payment_method_id': self.journal_id.outbound_payment_method_ids and self.journal_id.outbound_payment_method_ids[0].id,
            }
            if self.env.get('fiscalyears.periods',False) != False:
                periods = self.env['fiscalyears.periods'].search(
                    [('state', '=', 'open'),
                     ('start_date', '<=', fields.Date.today()),
                     ('end_date', '>=', fields.Date.today())])
                if periods:
                    dict['period_id'] = periods[0].id
                else:
                    raise ValidationError(_("No period found for date (%s)")%(fields.Date.today(),))
            self.env['account.payment'].create(dict)

        self.state = 'draft'

        self.tracker_ids.create({'invoice_id':self.id, 'state':self.state})
        return super(AccountInvoice, self).action_invoice_open()

    def action_invoice_draft(self):
        self.tracker_ids.unlink()
        return super(AccountInvoice, self).action_invoice_draft()


    '''def _get_aml_for_amount_residual(self):
        """ Get the aml to consider to compute the amount residual of invoices """
        self.ensure_one()
        if self.pay_now == 'pay_now':
            return []
        else:
            return super(AccountInvoice, self)._get_aml_for_amount_residual()

    @api.onchange('payment_journal_id', 'pay_now')
    def _onchange_payment_journal_id(self):
        return self._onchange_partner_id()

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        account_id = False
        company_id = self.company_id.id
        p = self.partner_id if not company_id else self.partner_id.with_context(force_company=company_id)
        type = self.type
        if p:
            rec_account = self.pay_now == 'pay_now' and self.payment_journal_id.default_debit_account_id or p.property_account_receivable_id
            pay_account = self.pay_now == 'pay_now' and self.payment_journal_id.default_credit_account_id or p.property_account_payable_id
            if not rec_account and not pay_account:
                action = self.env.ref('account.action_account_config')
                msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

            if type in ('in_invoice', 'in_refund'):
                account_id = pay_account.id
            else:
                account_id = rec_account.id

        self.account_id = account_id
        return res'''


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    vendor = fields.Char()
    invoice_no = fields.Char()
    invoice_date = fields.Date()
