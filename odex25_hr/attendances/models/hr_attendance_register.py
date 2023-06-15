# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _, exceptions


class HrAttendanceRegister(models.Model):
    _name = 'hr.attendance.register'
    _rec_name = 'register_date'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    action_type = fields.Selection(selection=[('sign_in', _('Sign In')),
                                              ('sign_out', _('Sign Out'))], string='Action Type')
    action_date = fields.Datetime(string='Attendance Date')
    from_hr_depart = fields.Boolean()
    department_id = fields.Many2one(related="employee_id.department_id", readonly=True)
    job_id = fields.Many2one(related="employee_id.job_id", readonly=True)
    employee_id = fields.Many2one('hr.employee', index=True, default=lambda item: item.get_user_id())

    note_text = fields.Text()
    register_date = fields.Date(string='Register Date', default=lambda self: fields.Date.today())
    state = fields.Selection(
        [('draft', _('Draft')),
         ('send', _('Send')),
         ('direct_manager', _('Direct Manager')),
         ('hr_manager', _('HR Manager')),
         ('refused', _('Refused'))], default="draft")
    date = fields.Date(string='Date')

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise exceptions.Warning(_('You can not delete record in state not in draft'))
        return super(HrAttendanceRegister, self).unlink()

    @api.constrains('action_date')
    def compute_date(self):
        for item in self:
            today = fields.Date.from_string(fields.Date.today())
            datee = item.action_date
            if datee:
                attendance_date = datetime.strptime(str(datee), "%Y-%m-%d %H:%M:%S")
                currnt_hour = datetime.now().hour + 3
                hour_attendance = attendance_date.hour + 3

                currnt_date = datetime.strptime(str(datee), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                deff_days = (today - fields.Date.from_string(currnt_date)).days
                if deff_days > 2:
                    raise exceptions.Warning(_('You can not Register Attendance Before Tow Days'))
                if deff_days < 0:
                    raise exceptions.Warning(_('You can not Register Attendance After Today'))
                # item.date = currnt_date
                priv_register = self.env['hr.attendance.register'].search([('employee_id', '=', item.employee_id.id),('id','!=',item.id)])
                for reg in priv_register:
                    date = datetime.strptime(reg.action_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                    if date == currnt_date:
                        raise exceptions.Warning(_('You can not Register Attendance More Than once in The Same day'))

                if currnt_date > item.register_date:
                   raise exceptions.Warning(_('You can not Register Attendance At Future Date'))

                if hour_attendance > currnt_hour:
                   raise exceptions.Warning(_('You can not Register Attendance Before The Time'))

    def draft_state(self):
        self.state = "draft"

    def button_submit(self):
        self.state = "send"

    def direct_manager(self):
        self.state = "direct_manager"

    def hr_manager(self):
        extract_date = datetime.strptime(str(self.action_date), "%Y-%m-%d %H:%M:%S").date()
        self.env['attendance.attendance'].create({
            'employee_id': self.employee_id.id,
            'name': self.action_date,
            'action': self.action_type,
            'action_date': self.action_date.date(),
            'action_type': 'manual',
        })

        self.state = "hr_manager"
        self.call_cron_function()

    def set_to_draft(self):
        for item in self:
            attendances = self.env['attendance.attendance'].search([('action_date', '=', item.action_date),
                                                                    ('employee_id', '=', item.employee_id.id)],
                                                                   order="name asc")
            for attendance in attendances:
                if attendance.name == item.action_date:
                    attendance.unlink()
        self.state = "draft"
        self.call_cron_function()

    def call_cron_function(self):
        date = datetime.strptime(str(self.action_date), "%Y-%m-%d %H:%M:%S")
        self.env['hr.attendance.transaction'].process_attendance_scheduler_queue(self.action_date, self.employee_id)

    def refused(self):
        self.state = "refused"

    def get_user_id(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if employee_id:
            return employee_id.id
        else:
            return False
