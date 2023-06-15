# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrPayrollRaise(models.Model):
    _name = 'hr.payroll.raise'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee annual raises"
    _order = "employee_id asc, id desc"

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, domain=[('state', '=', 'open')])
    # raise_date = fields.Date('Raise Date', default=lambda self: fields.Date.today(), required=True)
    application_date = fields.Date('Application Date', required=True)
    raise_type = fields.Selection(selection=[('annual', 'Annual'),('discrimination', 'Discrimination'),
                                             ('exceptional', 'Exceptional')
                                             ], string='Raise Type', required=True, default='exceptional')
    margin = fields.Float('Time Margin')
    deviation = fields.Float('Deviation in Days', compute='_compute_deviation', store=True, default=0)

    scale_id = fields.Many2one('hr.payroll.structure', 'Scale', domain=[('type', '=', 'scale')])
    level_id = fields.Many2one('hr.payroll.structure', 'Level', domain=[('type', '=', 'level')])
    group_id = fields.Many2one('hr.payroll.structure', 'Group', domain=[('type', '=', 'group')])
    degree_id = fields.Many2one('hr.payroll.structure', 'Degrees', domain=[('type', '=', 'degree')])

    nominated_degree_id = fields.Many2one('hr.payroll.structure', 'Nominated Degree', required=True,
                                          domain=[('type', '=', 'degree')])
    last_raise_date = fields.Date('Last Raise Date')
    next_raise_date = fields.Date('Next Raise Date')

    note = fields.Html('Notes')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('approve', 'Approved'),
                              ('refuse', 'Refused')], 'State', default='draft',track_visibility='always')

    last_raises = fields.Boolean(string='Last Raise', default=True, readonly=True)
    current_salary = fields.Float(string='Current Salary Amount', store=True)
    current_salary_insurance = fields.Float(string='Salary Insurance', store=True)

    percentage_bonus = fields.Boolean(string='Percentage Bonus')
    percentage_raises = fields.Float(string='Percentage Raises')

    new_salary = fields.Float(string='New Salary Amount', store=True)

    @api.onchange('employee_id','percentage_bonus','percentage_raises')
    def onchange_employee(self):
        self.nominated_degree_id = False
        if self.employee_id:
            self.scale_id = self.employee_id.salary_scale.id
            self.level_id = self.employee_id.salary_level.id
            self.group_id = self.employee_id.salary_group.id
            self.degree_id = self.employee_id.salary_degree.id
            self.last_raise_date = self.employee_id.degree_date
            self.current_salary = self.employee_id.contract_id.salary
            self.current_salary_insurance = self.employee_id.contract_id.salary_insurnce
            rs_dt = self.employee_id.degree_date and self.employee_id.degree_date or self.employee_id.first_hiring_date
            if rs_dt and self.employee_id.degree_date:
                ndate = fields.Date.from_string(rs_dt) + relativedelta(days=self.employee_id.salary_degree.time_margin
                                                                       ) or False
                self.next_raise_date = ndate

            if self.percentage_bonus==True:
               self.new_salary= (self.current_salary*self.percentage_raises)/100+self.current_salary

    @api.onchange('nominated_degree_id')
    def onchange_degree(self):
        if self.employee_id and self.nominated_degree_id and self.degree_id and \
                self.nominated_degree_id.sequence < self.degree_id.sequence:
            raise ValidationError(_('Sorry nominated degree %s is less than the current employee degree')
                                  % self.nominated_degree_id.name)

    @api.depends('nominated_degree_id', 'application_date')
    def _compute_deviation(self):
        for rec in self:
            if not rec.application_date: return
            if rec.nominated_degree_id and rec.degree_id:
                days_to_raise = 0
                degress_between = self.env['hr.payroll.structure'].search(
                    [('salary_scale_level_id', '=', rec.level_id.id),
                     ('salary_scale_group_id', '=', rec.group_id.id),
                     ('salary_scale_id', '=', rec.scale_id.id),
                     ('sequence', '>=', rec.degree_id.sequence),
                     ('sequence', '<', rec.nominated_degree_id.sequence)])
                for dg in degress_between:
                    days_to_raise += dg.time_margin

                degree_date = rec.employee_id.degree_date and rec.employee_id.degree_date or \
                              rec.employee_id.first_hiring_date
                if not degree_date:
                    return
                passed_days = rec.employee_id and \
                              (fields.Date.from_string(rec.application_date) - fields.Date.from_string(
                                  degree_date)).days or 0
                rec.deviation = passed_days - days_to_raise

                rs_dt = rec.employee_id.degree_date and rec.employee_id.degree_date or rec.employee_id.first_hiring_date
                if rs_dt and rec.employee_id.salary_degree:
                    ndate = fields.Date.from_string(rs_dt) + relativedelta(
                        days=rec.employee_id.salary_degree.time_margin) or False
                    rec.next_raise_date = ndate

    def act_confirm(self):
        if self.percentage_bonus==True and self.percentage_raises <= 0:
           raise ValidationError(_('Sorry, The Percentage Of Bonus Increase Must Be Greater Than Zero'))
        self.state = 'confirm'

    def act_approve(self):
        for rec in self:
            if not rec.percentage_bonus:
                rec.employee_id.degree_date = rec.application_date
                rec.employee_id.contract_id.salary_degree = rec.nominated_degree_id.id
                rec.employee_id.contract_id.salary = rec.nominated_degree_id.base_salary
                rec.employee_id.contract_id.salary_insurnce = rec.nominated_degree_id.base_salary
                last_raise = self.search([('employee_id', '=', rec.employee_id.id),
                                          ('id', '!=', rec.id),
                                          ('level_id', '=', rec.level_id.id),
                                          ('group_id', '=', rec.group_id.id),
                                          ('scale_id', '=', rec.scale_id.id),
                                          ('state', '=', 'approve')], order='application_date desc', limit=1)
                if last_raise:
                    last_raise.last_raises = False
            else:
                if rec.percentage_raises > 0:
                    # currnt_salary = rec.employee_id.contract_id.salary
                    rec.employee_id.contract_id.salary = rec.current_salary + (
                                rec.current_salary * rec.percentage_raises) / 100
                    rec.employee_id.contract_id.salary_insurnce = rec.employee_id.contract_id.salary
            rec.state = 'approve'

    def act_refuse(self):
        self.state = 'refuse'

    def act_reset(self):
        for rec in self:
            if not rec.last_raises:
                raise ValidationError(_('Sorry you can not set to Draft this Not last Raise'))
            rec.employee_id.contract_id.salary_degree = rec.degree_id.id
            last_raise = rec.search([('employee_id', '=', rec.employee_id.id),
                                     ('id', '!=', rec.id),
                                     ('level_id', '=', rec.level_id.id),
                                     ('group_id', '=', rec.group_id.id),
                                     ('scale_id', '=', rec.scale_id.id),
                                     # ('nominated_degree_id', '=', self.degree_id.id),
                                     ('state', '=', 'approve')], order='application_date desc', limit=1)
            rec.employee_id.degree_date = last_raise and last_raise.application_date or \
                                          rec.employee_id.first_hiring_date
            if last_raise:
                last_raise.last_raises = True
            rec.state = 'draft'

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('Sorry you can not delete a record that is not in draft state'))
            # if rec.state == 'draft' and rec.nomination_id and not self.env.context.get('permit_dlt', False):
            # raise ValidationError(_('Sorry you can not delete nomination record'))
            return super(HrPayrollRaise, self).unlink()

    def write(self, vals):
        res = super(HrPayrollRaise, self).write(vals)
        if 'state' in vals:
            for rec in self:
                if rec.nomination_id:
                    rec.nomination_id.check_raise_nominee()
