# -*- coding: utf-8 -*-
from __future__ import division

from datetime import datetime, timedelta

from odoo import models, fields, _, exceptions
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class HrAttendanceReport(models.Model):
    _name = 'hr.attendance.report'
    _rec_name = 'date_from'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date_from = fields.Date()
    date_to = fields.Date()
    line_ids = fields.One2many('hr.attendance.report.line', 'line_id')
    state = fields.Selection(
        [('draft', _('Draft')), ('generated', _('Generated')),
         # ('reviewed', _('Reviewed')),
         ('confirmed', _('HR Manager Approval')),
         ('approved', _('Approved')), ('refused', _('Refused'))], default="draft")
    calendar_ids = fields.Many2many('resource.calendar', string='Calendars')

    deduct_date_from = fields.Date()
    deduct_date_to = fields.Date()

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise exceptions.Warning(_('You can not delete record in state not in draft'))
        return super(HrAttendanceReport, self).unlink()

    def draft_state(self):
        self.state = "draft"

    def reviewed(self):
        self.state = "reviewed"

    def confirmed(self):
        self.state = "confirmed"

    def set_to_draft(self):
        for line in self.line_ids:
            if line.advantage_id:
                line.advantage_id.draft()
                line.advantage_id.unlink()
        self.line_ids.unlink()
        # self.write({'line_ids': [(5,)]})
        self.state = "draft"

    def approved(self):
        for line in self.line_ids:
            employee_contract = line.env['hr.contract'].search([('employee_id', '=', line.employee_name.id),
                                                                ('state', '=', 'program_directory')])
            if employee_contract and line.employee_name.finger_print:
                advantage_arc = line.env['contract.advantage'].create({
                    'benefits_discounts': line.employee_name.resource_calendar_id.deduction_rule.id,
                    'type': 'customize',
                    'date_from': self.deduct_date_from,
                    'date_to': self.deduct_date_to,
                    'amount': line.total_deduction,
                    'employee_id': line.employee_name.id,
                    'contract_advantage_id': line.employee_name.contract_id.id,
                    'out_rule': True,
                    'state': 'confirm',
                    'comments': 'Absence Deduction'})
                line.advantage_id = advantage_arc.id

        self.state = "approved"

    def refused(self):
        for line in self.line_ids:
            line.advantage_id.draft()
            line.advantage_id.unlink()
        self.state = "refused"

    def calcualte_flexible_transaction(self, transactions):
        planed_hours = sum(transactions.filtered(lambda t: t.public_holiday == False).mapped('plan_hours'))
        office_hours = sum(transactions.mapped('office_hours'))
        permission_hours = sum(transactions.filtered(
            lambda t: t.personal_permission_id != False).mapped('total_permission_hours'))
        mission_hours = sum(transactions.filtered(
            lambda t: t.official_id != False
                      and t.official_id.mission_type.duration_type == 'hours').mapped('total_mission_hours'))
        mission_by_days_hours = sum(transactions.filtered(
            lambda t: t.official_id != False
                      and t.official_id.mission_type.duration_type == 'days').mapped('total_mission_hours'))
        leave_hours = sum(transactions.filtered(lambda t: t.normal_leave == True).mapped('total_leave_hours'))
        working_hours = office_hours + permission_hours + mission_hours + mission_by_days_hours + leave_hours
        missed_hours = planed_hours - working_hours
        if missed_hours < 0:
            missed_hours = 0
        return {'leaves': leave_hours, 'missed_hours': missed_hours, 'mission_by_days': mission_by_days_hours}

    def generate_report(self):
        transaction_values = {}
        item_list, mixed_calendar_emps = [], []
        module = self.env['ir.module.module'].sudo()
        official_mission_module = module.search([('state', '=', 'installed'), ('name', '=', 'exp_official_mission')])
        personal_permission_module = module.search([('state', '=', 'installed'), ('name', '=', 'employee_requests')])
        holidays_module = module.search([('state', '=', 'installed'), ('name', '=', 'hr_holidays_public')])
        transaction_pool = self.env['hr.attendance.transaction']
        reason_pool = self.env['hr.reasons.lateness']
        domain = self._context.get('emp_id', False) and [('id', '=', self._context.get('emp_id'))] or []
        emps = self.env['hr.employee'].search(domain)
        trans_domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('attending_type', '=', 'in_cal')]
        if self.calendar_ids: trans_domain += [('calendar_id', 'in', self.calendar_ids.ids)]
        for employee in emps:
            missed_hours, wasted_hours, absent, total_mission, leaves, hours_per_day, count, \
                additional_hours = 0, 0, 0, 0, 0, 0, 0, 0
            emp_trans_dom = trans_domain.copy() + [('employee_id', '=', employee.id)]
            attendance_transaction = transaction_pool.search(emp_trans_dom)
            if len(attendance_transaction.mapped('calendar_id')) > 1:
                mixed_calendar_emps.append(employee.id)
                continue
            else:
                emp_calendar = attendance_transaction and attendance_transaction[0].calendar_id\
                               or employee.resource_calendar_id
            if emp_calendar.is_flexible:
                flexible_trans = attendance_transaction.filtered(lambda t: t.public_holiday == False)
                no_of_days = len(set(flexible_trans.mapped('date')))
                flexible_days = emp_calendar.number_of_flexi_days
                if no_of_days >= flexible_days:
                    ord_trans_dates = sorted(set(flexible_trans.mapped('date')),
                                             key=lambda x: datetime.strptime(x, DATE_FORMAT))
                    index = len(ord_trans_dates) > flexible_days and flexible_days - 1 or len(ord_trans_dates) - 1
                    df = fields.Date.from_string(self.date_from)
                    while no_of_days >= flexible_days:
                        dt = ord_trans_dates[index]
                        current_trans = attendance_transaction.filtered(lambda t: str(df) <= t.date <= str(dt))
                        hours_dict = self.calcualte_flexible_transaction(current_trans)
                        total_mission += hours_dict['mission_by_days']
                        missed_hours += hours_dict['missed_hours']
                        leaves += hours_dict['leaves']
                        additional_hours += hours_dict['additional_hours']
                        df = fields.Date.from_string(dt) + timedelta(1)
                        index = index + flexible_days > len(ord_trans_dates) and len(ord_trans_dates) or index + flexible_days
                        no_of_days -= flexible_days
                    else:
                        if no_of_days and no_of_days < flexible_days:
                            current_trans = attendance_transaction.filtered(lambda t: str(df) <= t.date <= self.date_to)
                            hours_dict = self.calcualte_flexible_transaction(current_trans)
                            total_mission += hours_dict['mission_by_days']
                            missed_hours += hours_dict['missed_hours']
                            leaves += hours_dict['leaves']
                            additional_hours += hours_dict['additional_hours']
                else:
                    hours_dict = self.calcualte_flexible_transaction(attendance_transaction)
                    missed_hours = hours_dict['missed_hours']
                    leaves, total_mission = hours_dict['leaves'], hours_dict['mission_by_days']
                working_hours_flexible_days = emp_calendar.total_flexible_hours
                values = {
                    'employee_name': employee.id,
                    'delay': 0.0,
                    'leave': leaves,
                    'additional_hours': 0.0,
                    'exists': 0.0,
                    'extra_break_duration': 0.0,
                    'absent': missed_hours,
                    'mission_by_days': total_mission,
                    'absent_days_by_hr': 0.0,
                    'total_hours': missed_hours,
                    'dummy_field': missed_hours,
                    'total_amount': employee.contract_id.total_allowance,
                    'amount_per_hour': employee.contract_id.total_allowance / working_hours_flexible_days,
                    'total_deduction': missed_hours * (
                                employee.contract_id.total_allowance / working_hours_flexible_days)
                }
                item_list.append(values)
            elif not emp_calendar.is_flexible:
                lateness_reasons = reason_pool.search([('latest_date', '>=', self.date_from),
                                                       ('latest_date', '<=', self.date_to),
                                                       ('employee_id', '=', employee.id),
                                                       ('state', '=', 'hr_manager')])
                emp_trans = attendance_transaction.filtered(lambda t: t.public_holiday == False)
                for attendance in emp_trans:
                    lateness, early_exist, extra_break_duration, hours, additional_hours = 0.0, 0.0, 0.0, 0.0, 0.0
                    total_permission, total_mission_by_hour, total_mission_by_day, total_leaves = 0.0, 0.0, 0.0, 0.0
                    total_absent, lateness_hours_by_hr, get_total_amount = 0.0, 0.0, 0.0
                    transaction_values['id'], transaction_values['name'] = attendance.employee_id.id, attendance.employee_id.name
                    total_hours_for_two_shifts = emp_calendar.shift_one_working_hours + \
                                                 emp_calendar.shift_two_working_hours
                    if lateness_reasons:
                        if attendance.lateness > 0.0 or attendance.early_exit > 0.0:
                            for late in lateness_reasons:
                                if attendance.date == late.latest_date:
                                    lateness_hours_by_hr += (attendance.lateness + attendance.early_exit)
                    if attendance.approve_lateness: lateness += attendance.lateness
                    if attendance.approve_exit_out: early_exist += attendance.early_exit
                    if personal_permission_module and attendance.approve_personal_permission:
                        total_permission += attendance.total_permission_hours
                    if official_mission_module and attendance.is_official:
                        if attendance.official_id.mission_type.duration_type == 'days':
                            total_mission_by_day += attendance.total_mission_hours
                        else:
                            total_mission_by_hour += attendance.total_mission_hours
                    if holidays_module and attendance.normal_leave:
                        total_leaves += attendance.total_leave_hours
                    hours += attendance.official_hours
                    extra_break_duration += attendance.break_duration
                    additional_hours += attendance.additional_hours
                    if attendance.is_absent:
                        total_absent += attendance.plan_hours
                        if attendance.calendar_id.is_full_day:
                            total_absent += attendance.calendar_id.break_duration
                        elif attendance.sequence == 1:
                            total_absent += attendance.calendar_id.shift_one_break_duration
                        elif attendance.sequence == 2:
                            total_absent += attendance.calendar_id.shift_two_break_duration
                    else:
                        working_hours = total_permission + total_mission_by_hour + hours + attendance.carried_hours
                        absence_hours = attendance.plan_hours - working_hours
                        total_absent += absence_hours > 0 and absence_hours or 0
                    if total_absent == 0:
                        get_total_hours = (
                                                      lateness + early_exist + extra_break_duration + total_absent) - lateness_hours_by_hr
                    else:
                        get_total_hours = (total_absent - lateness_hours_by_hr)
                    if get_total_hours < 0:
                        get_total_hours = 0
                    if attendance.employee_id.contract_id.state == 'program_directory':
                        get_total_amount = attendance.employee_id.contract_id.total_allowance
                    if emp_calendar.is_full_day:
                        working_hours_per_week = emp_calendar.working_hours * emp_calendar.working_days
                        get_amount_per_hour = get_total_amount / working_hours_per_week
                    else:
                        get_amount_per_hour = get_total_amount / (
                                    total_hours_for_two_shifts * emp_calendar.working_days)
                    values = {
                        'employee_name': attendance.employee_id.id,
                        'delay': lateness,
                        'leave': total_leaves,
                        'exists': early_exist,
                        'extra_break_duration': extra_break_duration,
                        'absent': total_absent,
                        'mission_by_days': total_mission_by_day,
                        'absent_days_by_hr': lateness_hours_by_hr,
                        'total_hours': get_total_hours,
                        'dummy_field': get_total_hours,
                        'total_amount': get_total_amount,
                        'amount_per_hour': get_amount_per_hour,
                        'total_deduction': get_total_hours * get_amount_per_hour,
                        'additional_hours': additional_hours
                    }
                    item_list.append(values)
        from itertools import groupby, tee
        from operator import itemgetter
        grouper = itemgetter("employee_name")
        result = []
        for key, grp in groupby(sorted(item_list, key=grouper), grouper):
            if not isinstance(key, tuple):
                key = [key]
            temp_dict = dict(zip(["employee_name"], key))
            grp1, grp2, grp3, grp4, grp5, grp6, grp7, grp8, grp9, grp10, grp11, grp12, grp13, grp14, grp15 = tee(grp, 15)

            temp_dict["delay"] = sum(item["delay"] for item in grp1)
            temp_dict["leave"] = sum(item1["leave"] for item1 in grp2)
            temp_dict["mission_by_days"] = sum(item1["mission_by_days"] for item1 in grp14)
            temp_dict["absent"] = sum(item1["absent"] for item1 in grp3) - (
                        temp_dict["leave"] + temp_dict["mission_by_days"])
            temp_dict["exists"] = sum(item1["exists"] for item1 in grp4)
            temp_dict["extra_break_duration"] = sum(item1["extra_break_duration"] for item1 in grp5)
            temp_dict["absent_days_by_hr"] = sum(item1["absent_days_by_hr"] for item1 in grp6)
            temp_dict["total_hours"] = sum(item["total_hours"] for item in grp7) - (
                        temp_dict["leave"] + temp_dict["mission_by_days"])
            temp_dict["dummy_field"] = sum(item["dummy_field"] for item in grp13)
            temp_dict["total_amount"] = sum(item["total_amount"] for item in grp8) / len(list(grp9))
            temp_dict["amount_per_hour"] = sum(item["amount_per_hour"] for item in grp10) / len(list(grp11))

            ############# re chick total_deduction

            temp_dict["total_deduction"] = temp_dict["absent"]*temp_dict["amount_per_hour"] 
            #temp_dict["total_deduction"] = sum(item["total_deduction"] for item in grp12)
            temp_dict["additional_hours"] = sum(item["additional_hours"] for item in grp15)
            result.append(temp_dict)
        self.write({'line_ids': [(0, 0, val) for val in result]})
        self.state = "generated"
        if mixed_calendar_emps:
            self.manage_mixed_calendar(mixed_calendar_emps)

    def manage_mixed_calendar(self, emp_calendars):
        for emp in emp_calendars:
            trans = self.env['hr.attendance.transaction'].search([('date', '>=', self.date_from),
                                                                  ('date', '<=', self.date_to),
                                                                  ('employee_id', '=', emp)])
            calendar_ids = trans.mapped('calendar_id').ids
            recs = self.env['hr.attendance.report']
            for cal in calendar_ids:
                tdates = list(set(trans.filtered(lambda l: l.calendar_id.id == cal).mapped('date')))
                tdates.sort()
                ldate = fields.Date.from_string(tdates[0]) + timedelta(len(tdates) - 1)
                if ldate == fields.Date.from_string(tdates[-1]):
                    rec = self.create({'date_from': tdates[0], 'date_to': tdates[-1]})
                    rec.with_context(emp_id=emp).generate_report()
                    recs += rec
                else:
                    ranges, date_range, base = [], [], tdates.pop(0)
                    date_range.append(base)
                    bdate = fields.Date.from_string(base) + timedelta(1)
                    for dt in tdates:
                        if bdate == fields.Date.from_string(dt):
                            date_range.append(dt)
                            bdate += timedelta(1)
                            if dt == tdates[-1]:
                                ranges.append(date_range)
                        else:
                            ranges.append(date_range)
                            date_range, bdate = [dt], fields.Date.from_string(dt) + timedelta(1)
                    for range in ranges:
                        rec = self.create({'date_from': range[0], 'date_to': range[-1]})
                        rec.with_context(emp_id=emp).generate_report()
                        recs += rec
            main_rec = recs[0]
            sum_recs = recs.filtered(lambda r: r.id != main_rec.id)
            sum_line = main_rec.line_ids[0]
            sum_line.write({
                'line_id': self.id,
                'delay': sum_line.delay + sum(sum_recs.mapped('line_ids.delay')),
                'leave': sum_line.leave + sum(sum_recs.mapped('line_ids.leave')),
                'absent': sum_line.absent + sum(sum_recs.mapped('line_ids.absent')),
                'exists': sum_line.exists + sum(sum_recs.mapped('line_ids.exists')),
                'total_hours': sum_line.total_hours + sum(sum_recs.mapped('line_ids.total_hours')),
                'dummy_field': sum_line.dummy_field + sum(sum_recs.mapped('line_ids.dummy_field')),
                'total_deduction': sum_line.total_deduction + sum(sum_recs.mapped('line_ids.total_deduction')),
                'absent_days_by_hr': sum_line.absent_days_by_hr + sum(sum_recs.mapped('line_ids.absent_days_by_hr')),
                'mission_by_days': sum_line.mission_by_days + sum(sum_recs.mapped('line_ids.mission_by_days')),
                'extra_break_duration': sum_line.extra_break_duration + sum(
                    sum_recs.mapped('line_ids.extra_break_duration')),
                'additional_hours': sum_line.additional_hours + sum(sum_recs.mapped('line_ids.additional_hours')),
            })

            recs.unlink()
