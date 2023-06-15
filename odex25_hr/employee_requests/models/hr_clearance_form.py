# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class HrClearanceForm(models.Model):
    _name = 'hr.clearance.form'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    from_hr_department = fields.Boolean()
    # employee_id = fields.Many2one(comodel_name='hr.employee')
    date = fields.Date(default=lambda self: fields.Date.today())
    date_deliver_work = fields.Date()
    job_id = fields.Many2one(related='employee_id.job_id', readonly=True)
    department_id = fields.Many2one(related='employee_id.department_id', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employee Id', default=lambda item: item.get_user_id(),
                                  domain=[('state', '=', 'open')])

    clearance_type = fields.Selection(selection=[("vacation", _("Vacation Clearance")),
                                                 ("final", _("Final Clearance"))], default='final')
    work_delivered = fields.Text()
    super_mg = fields.Selection(selection=[("approve", _("Approve")),
                                           ("refuse", _("Refuse"))], default='approve')
    super_refuse_cause = fields.Text(default='/')
    direct_mg = fields.Selection(selection=[("approve", _("Approve")),
                                            ("refuse", _("Refuse"))], default='approve')
    direct_refuse_cause = fields.Text(default='/')
    hr_mg = fields.Selection(selection=[("approve", _("Approve")),
                                        ("refuse", _("Refuse"))], default='approve')
    hr_refuse_cause = fields.Text(default='/')

    it_mg = fields.Selection(selection=[("approve", _("Approve")),
                                        ("refuse", _("Refuse"))], default='approve')
    it_refuse_cause = fields.Text(default='/')

    state = fields.Selection(selection=[("draft", _("Draft")),
                                        ("submit", _("Submitted")),
                                        ("direct_manager", _("Direct Manager")),
                                        ('info_system', _('IT Department')),
                                        ('admin_manager', _('Admin Affairs')),
                                        ("wait", _("Finance Approvals")),
                                        ("done", _("HR Manager")),
                                        ("refuse", _("Refuse"))], default='draft', tracking=True)

    bank_attachment_id = fields.Many2many('ir.attachment', 'clearance_form_rel', 'bank_id', 'attach_id',
                                          string="Attachment",
                                          help='You can attach the copy of your document', copy=False)
    bank_comments = fields.Text()

    company_id = fields.Many2one('res.company',string="Company", default=lambda self: self.env.user.company_id)

    @api.constrains('employee_id')
    def chick_hiring_date(self):
        for item in self:
            if item.employee_id:
                if not item.employee_id.first_hiring_date:
                    raise exceptions.Warning(_('You can not Request Clearance The Employee have Not First Hiring Date'))

    def draft(self):

        self.state = "draft"

    def submit(self):
        # Check if exp_custody_petty_cash module is installed
        Module = self.env['ir.module.module'].sudo()
        modules = Module.search([('state', '=', 'installed'), ('name', '=', 'exp_custody_petty_cash')])

        if modules:
            # Check if employee has Employee Custody not in state Return done
            employee_custody = self.env['custom.employee.custody'].search(
                [('employee_id', '=', self.employee_id.id), ('state', 'in', ['submit', 'direct', 'admin', 'approve'])])
            if len(employee_custody) > 0:
                raise exceptions.Warning(
                    _(
                        'You can not Employee Clearance %s employee custody not in state Return Done for %s please '
                        'reconcile it') % (
                        self.employee_id.name, len(employee_custody)))

            # Check if employee has Employee Petty Cash Payment not in state Return done
            employee_petty_cash_payment = self.env['petty.cash.payment'].search(
                [('employee_id', '=', self.employee_id.id),
                 ('state', 'in', ['submit', 'direct', 'fm', 'ceo', 'accepted', 'validate'])])
            if len(employee_petty_cash_payment) > 0:
                raise exceptions.Warning(
                    _('You can not Employee Clearance %s employee petty cash payment not in state Return Done for %s '
                      'please reconcile it') % (
                        self.employee_id.name, len(employee_petty_cash_payment)))

        '''for item in self:
            mail_content = "Hello I'm", item.employee_id.name, " request to Clearance Of ", item.clearance_type,"Please approved thanks."
            main_content = {
                   'subject': _('Request clearance-%s Employee %s') % (item.clearance_type, item.employee_id.name),
                   'author_id': self.env.user.partner_id.id,
                   'body_html': mail_content,
                   'email_to': item.department_id.email_manager,
                }
            self.env['mail.mail'].create(main_content).send()'''
        self.state = "submit"

    def direct_manager(self):
        # Check if exp_custody_petty_cash module is installed
        Module = self.env['ir.module.module'].sudo()
        modules = Module.search([('state', '=', 'installed'), ('name', '=', 'exp_custody_petty_cash')])

        if modules:
            # Check if employee has Employee Custody not in state Return done
            employee_custody = self.env['custom.employee.custody'].search(
                [('employee_id', '=', self.employee_id.id), ('state', 'in', ['submit', 'direct', 'admin', 'approve'])])
            if len(employee_custody) > 0:
                raise exceptions.Warning(
                    _('You can not Employee Clearance "%s" employee custody not in state Return '
                      'Done for "%s" please reconcile it') % (len(employee_custody), self.employee_id.name))

            # Check if employee has Employee Petty Cash Payment not in state Return done
            employee_petty_cash_payment = self.env['petty.cash.payment'].search(
                [('employee_id', '=', self.employee_id.id), ('state', 'in', ['submit', 'direct', 'fm', 'ceo',
                                                                             'accepted', 'validate'])])
            if len(employee_petty_cash_payment) > 0:
                raise exceptions.Warning(
                    _('You can not Employee Clearance "%s" employee petty cash payment not in state Return '
                      'Done for "%s" please reconcile it') % (
                        len(employee_petty_cash_payment), self.employee_id.name))
        self.state = "direct_manager"

    def info_system(self):
        self.state = "info_system"

    def admin_manager(self):
        self.state = "admin_manager"

    def wait(self):

        for item in self:

            if not item.bank_attachment_id and item.clearance_type != 'vacation':
                raise exceptions.Warning(_('The Clearance to be completed after the Bank Clearance Attachment'))
        self.state = "wait"


    def done(self):
        if not self.bank_attachment_id:
            raise exceptions.Warning(_('The Clearance to be completed after the Bank Clearance Attachment'))

        self.employee_id.write({'is_calender': True})
        self.state = "done"

    def refuse(self):
        self.state = "refuse"

    def get_user_id(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if employee_id:
            return employee_id.id
        else:
            return False

    def unlink(self):
        for i in self:
            if i.state != 'draft':
                raise exceptions.Warning(_('You can not delete record in state not in draft'))
        return super(HrClearanceForm, self).unlink()
