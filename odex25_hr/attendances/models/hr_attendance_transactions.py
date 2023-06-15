# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

from odoo.exceptions import UserError


class HrAttendanceTransactions(models.Model):
    _name = 'hr.attendance.transaction'
    _rec_name = 'employee_id'

    date = fields.Date(string='Day')
    lateness = fields.Float(compute='get_hours')
    early_exit = fields.Float(compute='get_hours')
    is_absent = fields.Boolean(string='Absent', compute='get_hours')
    sign_in = fields.Float()
    sign_out = fields.Float()
    approve_exit_out = fields.Boolean(string='Approve Early Exit', compute='get_hours')
    approve_lateness = fields.Boolean(string='Approve Lateness', compute='get_hours')
    employee_id = fields.Many2one('hr.employee', 'Employee Name', default=lambda item: item.get_user_id(), index=True)
    break_duration = fields.Float(string='Break Duration', default=0)
    total_absent_hours = fields.Float(compute='get_hours')
    calendar_id = fields.Many2one('resource.calendar', 'Calendar', readonly=True)
    office_hours = fields.Float(string='Attending Hours', default=0)
    official_hours = fields.Float(string='Official Hours', default=0)
    plan_hours = fields.Float(string='Planned Hours', default=0)
    carried_hours = fields.Float(string='Carried Hours', default=0)
    temp_exit = fields.Float(string='Temporary Exit Hours')
    temp_lateness = fields.Float(string='Temporary Lateness Hours')
    additional_hours = fields.Float(compute='get_additional_hours', string='Additional Hours', default=0)

    sequence = fields.Integer()
    attending_type = fields.Selection([('in_cal', 'within Calendar'),
                                       ('out_cal', 'out Calendar')], string='Attending Type', default="in_cal")

    def get_additional_hours(self):
        for rec in self:
            rec.additional_hours = 0
            if rec.office_hours > rec.plan_hours:
                rec.additional_hours = rec.office_hours - rec.plan_hours

    def get_hours(self):
        module = self.env['ir.module.module'].sudo()
        official_mission_module = module.search([('state', '=', 'installed'), ('name', '=', 'exp_official_mission')])
        holidays_module = module.search([('state', '=', 'installed'), ('name', '=', 'hr_holidays_public')])
        for item in self:
            item.is_absent = False
            item.approve_exit_out = False
            item.is_official = False
            item.total_absent_hours = 0
            item.official_id = False
            item.total_mission_hours = 0.0
            item.approve_personal_permission = False
            item.personal_permission_id = False
            item.total_permission_hours = 0.0
            item.approve_lateness = False
            item.lateness = False
            item.early_exit = False
            item.total_absent_hours = 0
            if item.attending_type == 'out_cal' \
                    or holidays_module and (item.public_holiday or item.normal_leave) \
                    or official_mission_module and item.is_official and item.official_id.mission_type.duration_type == 'days':
                item.write({'temp_lateness': 0.0, 'temp_exit': 0.0, 'break_duration': 0.0, 'is_absent': False})
                if holidays_module and (item.public_holiday or item.normal_leave):
                    item.write({'is_official': False, 'official_id': False, 'total_mission_hours': 0.0,
                                'approve_personal_permission': False, 'personal_permission_id': False,
                                'total_permission_hours': 0.0})
            else:
                # item.write({'temp_lateness': 0.0, 'temp_exit': 0.0, 'break_duration': 0.0, 'is_absent': False})
                day_trans = self.search([('date', '=', item.date),
                                         ('attending_type', '=', 'in_cal'),
                                         ('employee_id', '=', item.employee_id.id)])
                working_hours = sum(day_trans.mapped('official_hours')) \
                    + sum(day_trans.mapped('total_mission_hours')) \
                    + sum(day_trans.mapped('total_permission_hours'))
                if working_hours < item.calendar_id.end_sign_in and not item.calendar_id.is_flexible \
                        or item.calendar_id.is_flexible and working_hours == 0.0:
                    day_trans.update({'is_absent': True})
            if item.calendar_id.is_flexible:
                item.write({'temp_lateness': 0.0, 'temp_exit': 0.0, 'official_hours': item.office_hours})
            if item.temp_lateness:
                item.approve_lateness = True
            if item.temp_exit:
                item.approve_exit_out = True
            if item.break_duration and item.calendar_id.break_duration:
                # item.write({'break_duration': item.break_duration - item.calendar_id.break_duration})  #TODO
                item.write({'break_duration': item.break_duration})
            if item.break_duration < 0:
                item.break_duration = 0
            item.lateness = item.temp_lateness
            item.early_exit = item.temp_exit

    def get_sign_time(self, sign):
        ''' Func: return time as float considering timezone(fixed 3)'''

        # DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        TIME_FORMAT = "%H:%M:%S"
        TIME_ZONE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
        sign_offsit = datetime.strptime(str(sign), DATETIME_FORMAT) + timedelta(hours=3)
        sign_zone = datetime.strptime(sign_offsit.strftime(TIME_ZONE_FORMAT), TIME_ZONE_FORMAT)
        return round(datetime.strptime(sign_zone.strftime(TIME_FORMAT), TIME_FORMAT).time().hour +
                     datetime.strptime(sign_zone.strftime(TIME_FORMAT), TIME_FORMAT).time().minute / 60.0, 2), sign_zone

    def convert_float_2time(self, time, date=None):
        hour, minute = divmod(time * 60, 60)
        if date:
            if not isinstance(date, datetime): date = fields.Datetime.from_string(date)
            return date.replace(hour=int(hour), minute=int(minute), second=0) - timedelta(hours=3)
        return hour, minute

    def get_day_timing(self, calendar, weekday, wkd_date):
        planed_hours = {'one': 0, 'two': 0}
        if calendar.is_full_day:
            time_list = [0 for i in range(4)]
            sp_timing = self.get_speacial_day_timing(calendar, weekday, wkd_date)
            planed_hours['one'] = (sp_timing and sp_timing.working_hours or calendar.working_hours) - calendar.break_duration
            time_list[0] = sp_timing and sp_timing.start_sign_in or calendar.full_min_sign_in
            time_list[1] = sp_timing and sp_timing.end_sign_in or calendar.full_max_sign_in
            time_list[2] = sp_timing and sp_timing.start_sign_out or calendar.full_min_sign_out
            time_list[3] = sp_timing and sp_timing.end_sign_out or calendar.full_max_sign_out
        else:
            time_list = [0 for i in range(8)]
            one_sp_timing = self.get_speacial_day_timing(calendar, weekday, wkd_date, 'one')
            planed_hours['one'] = (one_sp_timing and one_sp_timing.working_hours or calendar.shift_one_working_hours) \
                                  - calendar.shift_one_break_duration
            two_sp_timing = self.get_speacial_day_timing(calendar, weekday, wkd_date, 'two')
            planed_hours['two'] = (two_sp_timing and two_sp_timing.working_hours or calendar.shift_two_working_hours) \
                                  - calendar.shift_two_break_duration
            time_list[0] = one_sp_timing and one_sp_timing.start_sign_in or calendar.shift_one_min_sign_in
            time_list[1] = one_sp_timing and one_sp_timing.end_sign_in or calendar.shift_one_max_sign_in
            time_list[2] = one_sp_timing and one_sp_timing.start_sign_out or calendar.shift_one_min_sign_out
            time_list[3] = one_sp_timing and one_sp_timing.end_sign_out or calendar.shift_one_max_sign_out
            time_list[4] = two_sp_timing and two_sp_timing.start_sign_in or calendar.shift_two_min_sign_in
            time_list[5] = two_sp_timing and two_sp_timing.end_sign_in or calendar.shift_two_max_sign_in
            time_list[6] = two_sp_timing and two_sp_timing.start_sign_out or calendar.shift_two_min_sign_out
            time_list[7] = two_sp_timing and two_sp_timing.end_sign_out or calendar.shift_two_max_sign_out
        return time_list, planed_hours

    def get_speacial_day_timing(self, calender, weekday, at_date, shift=None):
        sp_days = shift and calender.special_days_partcial or calender.special_days
        for spday in sp_days:
            if spday.name.lower() == weekday and ((shift and spday.shift == shift) or (not shift and True)):
                if spday.date_from and spday.date_to \
                        and str(at_date) >= spday.date_from and str(at_date) <= spday.date_to:
                    return spday
                elif spday.date_from and not spday.date_to and str(at_date) >= spday.date_from:
                    return spday
                elif not spday.date_from and spday.date_to and str(at_date) <= spday.date_to:
                    return spday
                elif not spday.date_from and not spday.date_to:
                    return spday

    def one_day_noke(self, noke_calendar):
        if noke_calendar.is_full_day:
            if noke_calendar.full_min_sign_in <= noke_calendar.full_max_sign_in \
                    < noke_calendar.full_min_sign_out <= noke_calendar.full_max_sign_out: return True
            return False
        else:
            if noke_calendar.shift_one_min_sign_in <= noke_calendar.shift_one_max_sign_in \
                    < noke_calendar.shift_one_min_sign_out <= noke_calendar.shift_one_max_sign_out \
                    < noke_calendar.shift_two_min_sign_in <= noke_calendar.shift_two_max_sign_in \
                    < noke_calendar.shift_two_min_sign_out <= noke_calendar.shift_two_max_sign_out: return True
            return False

    def noke_time_2date(self, time, noke_dt, calendar):
        last_nt = calendar[0]
        if calendar[0] < last_nt:
            noke_dt += timedelta(1)
        if time == 'one_max_in':
            return self.convert_float_2time(calendar[1], noke_dt)
        last_nt = calendar[1]
        if calendar[2] < last_nt:
            noke_dt += timedelta(1)
        if time == 'one_min_out':
            return self.convert_float_2time(calendar[2], noke_dt)
        last_nt = calendar[2]
        if calendar[3] < last_nt:
            noke_dt += timedelta(1)
        if time == 'one_max_out':
            return self.convert_float_2time(calendar[3], noke_dt)
        last_nt = calendar[3]
        if calendar[4] < last_nt:
            noke_dt += timedelta(1)
        if time == 'two_min_in':
            return self.convert_float_2time(calendar[4], noke_dt)
        last_nt = calendar[4]
        if calendar[5] < last_nt:
            noke_dt += timedelta(1)
        if time == 'two_max_in':
            return self.convert_float_2time(calendar[5], noke_dt)
        last_nt = calendar[5]
        if calendar[6] < last_nt:
            noke_dt += timedelta(1)
        if time == 'two_min_out':
            return self.convert_float_2time(calendar[6], noke_dt)
        last_nt = calendar[6]
        if calendar[7] < last_nt:
            noke_dt += timedelta(1)
        if time == 'two_max_out':
            return self.convert_float_2time(calendar[7], noke_dt)

    def prepare_shift(self, at_device, dt, signs_in, signs_out, min_in_dt, max_in_dt, min_out_dt, max_out_dt,
                      shift_dict, next_min_in_dt=None):
        attending_periods, linked_out_ids = [], []
        office_hours, official_hours, break_hours = 0, 0, 0
        at_dict = {'in': 0.0, 'out': 0.0, 'creep': 0}
        if signs_in:
            if not signs_out:
                at_dict['in'] = fields.Datetime.from_string(signs_in[0].name)
                if at_device:
                    at_dict['checkin_device_id'] = signs_in[0].device_id and signs_in[0].device_id.id or False
                    at_dict['checkout_device_id'] = False
                attending_periods.append(at_dict)
                linked_out_ids.append(signs_in[0].id)
            else:
                signs_time = []
                last_official_sign = True
                for sin in signs_in:
                    in_dt = fields.Datetime.from_string(sin.name)
                    for out in signs_out:
                        out_dt = fields.Datetime.from_string(out.name)
                        if signs_time and in_dt < last_out:
                            continue
                        if out_dt >= in_dt and out_dt >= min_in_dt \
                                and ((linked_out_ids and out.id not in linked_out_ids) or not linked_out_ids):
                            creep = next_min_in_dt \
                                    and (out_dt > next_min_in_dt and (out_dt - next_min_in_dt).seconds / 60 / 60) or 0.0
                            at_dic = {'in': in_dt, 'out': out_dt, 'creep': creep}
                            if at_device:
                                at_dic['checkin_device_id'] = sin.device_id and sin.device_id.id or False
                                at_dic['checkout_device_id'] = out.device_id and out.device_id.id or False
                            attending_periods.append(at_dic)
                            at_dic = {}
                            last_out = out_dt
                            linked_out_ids.append(out.id)
                            signs_time.append(in_dt)
                            signs_time.append(out_dt)
                            office_hours += (out_dt - in_dt).seconds / 60 / 60
                            if out_dt <= max_out_dt:
                                official_hours += (out_dt - in_dt).seconds / 60 / 60
                            elif out_dt > max_out_dt and last_official_sign:
                                official_hours += (max_out_dt - in_dt).seconds / 60 / 60
                                last_official_sign = False
                            break
        else:
            if next_min_in_dt:
                signed = False
                for out in signs_out:
                    out_dt = fields.Datetime.from_string(out.name)
                    if out_dt < next_min_in_dt:
                        one_out_dt = out_dt
                        checkout_device = out.device_id
                        linked_out_ids.append(out.id)
                        signed = True
                    else:
                        break
                if not signed:
                    return
                at_dict['out'] = one_out_dt
                if at_device:
                    at_dict['checkin_device_id'] = False
                    at_dict['checkout_device_id'] = checkout_device and checkout_device.id or False
                attending_periods.append(at_dict)
            else:
                at_dict['out'] = fields.Datetime.from_string(signs_out[-1].name)
                if at_device:
                    at_dict['checkin_device_id'] = False
                    at_dict['checkout_device_id'] = signs_out[-1].device_id and signs_out[-1].device_id.id or False
                attending_periods.append(at_dict)
                linked_out_ids.append(signs_out[-1].id)
        if at_device:
            shift_dict['checkin_device_id'] = attending_periods[0]['checkin_device_id']
            shift_dict['checkout_device_id'] = attending_periods[-1]['checkout_device_id']
        sign_in, sign_out = attending_periods[0]['in'], attending_periods[-1]['out']

        shift_dict['sign_in'] = sign_in and self.get_sign_time(fields.Datetime.to_string(sign_in))[0] or 0.0
        shift_dict['sign_out'] = sign_out and self.get_sign_time(fields.Datetime.to_string(sign_out))[0] or 0.0
        shift_dict['sign_in_dt'] = sign_in and sign_in or 0.0
        shift_dict['sign_out_dt'] = sign_out and sign_out or 0.0
        shift_dict['temp_lateness'] = sign_in and sign_out and (sign_in > max_in_dt
                                                                and round((sign_in - min_in_dt).seconds / 60 / 60,
                                                                          2)) or 0.0
        shift_dict['temp_exit'] = sign_in and sign_out and (sign_out < min_out_dt
                                                            and round((max_out_dt - sign_out).seconds / 60 / 60,
                                                                      2)) or 0.0
        shift_dict['break_duration'] = 0.0
        shift_dict['office_hours'], shift_dict['official_hours'] = office_hours, official_hours
        if sign_in and sign_out and ((next_min_in_dt and sign_in > max_out_dt and sign_out < next_min_in_dt)
                                     or (not next_min_in_dt and sign_in > max_out_dt)):
            shift_dict['attending_type'] = 'out_cal'
        if sign_in or sign_out == 0: shift_dict['is_absent'] = True
        if len(attending_periods) > 1:
            break_periods = []
            del signs_time[0]
            del signs_time[-1]
            for inx, sign_time in enumerate(signs_time):
                if inx % 2 == 0:
                    break_start = sign_time
                else:
                    break_hours += round((sign_time - break_start).seconds / 60 / 60, 2)
                    break_periods.append({'break_start': break_start, 'break_end': sign_time})
            shift_dict['break_duration'] = break_hours
        creep = round(attending_periods[-1]['creep'], 2)
        if break_hours:
            return {'shift': shift_dict, 'out_ids': linked_out_ids, 'creep': creep, 'break_periods': break_periods}
        return {'shift': shift_dict, 'out_ids': linked_out_ids, 'creep': creep}

    def manage_permission(self, trans_id, shift_in, shift_out, sign_in, sign_out, breaks, state=None):
        trans, feedback = self.browse(trans_id)[0], []
        if trans.personal_permission_id:
            trans.update(
                {'approve_personal_permission': False, 'personal_permission_id': False, 'total_permission_hours': 0.0})
        permissions = self.env['hr.personal.permission'].search(
            [('state', '=', 'approve'), ('employee_id', '=', trans.employee_id.id),
             '|', '|',
             '&', ('date_to', '<=', str(shift_out)), ('date_to', '>=', str(shift_in)),
             '&', ('date_from', '<=', str(shift_out)), ('date_from', '>=', str(shift_in)),
             '&', ('date_from', '<=', str(shift_in)), ('date_to', '>=', str(shift_out))
             ])
        if permissions:
            for perm in permissions:
                perm_time = 0
                perm_df = fields.Datetime.from_string(perm.date_from)
                perm_dt = fields.Datetime.from_string(perm.date_to)
                if trans.sign_in == 0.0 or trans.sign_out == 0.0:
                    perm_dic = {'approve_personal_permission': True,
                                'personal_permission_id': perm.id,
                                'total_permission_hours': perm.duration}
                    if state != 'check': trans.update(perm_dic)
                    if state is not None:
                        # perm_dic.update({ 'personal_permission_id': perm.id,'perm_start': perm_start, 'perm_end': perm_end})
                        feedback.append(
                            {'perm_id': perm.id, 'perm_start': perm_df, 'perm_end': perm_dt, 'type': 'all'})
                    continue
                if trans.temp_lateness:
                    if perm_df <= shift_in and perm_dt >= sign_in:
                        perm_time = round((sign_in - shift_in).seconds / 60 / 60, 2)
                        perm_start, perm_end = shift_in, sign_in
                    elif perm_df <= shift_in and perm_dt < sign_in and perm_dt > shift_in:
                        perm_time = round((perm_dt - shift_in).seconds / 60 / 60, 2)
                        perm_start, perm_end = shift_in, perm_dt
                    elif (perm_df > shift_in and perm_dt < sign_in) or sign_in == 0.0 or sign_out == 0.0:
                        perm_time = round((perm_dt - perm_df).seconds / 60 / 60, 2)
                        perm_start, perm_end = perm_df, perm_dt
                    elif perm_df < sign_in and perm_df > shift_in and perm_dt >= sign_in:
                        perm_time = round((sign_in - perm_df).seconds / 60 / 60, 2)
                        perm_start, perm_end = perm_df, sign_in
                    if perm_time:
                        perm_dic = {'approve_personal_permission': True,
                                    'personal_permission_id': perm.id,
                                    'total_permission_hours': perm_time,
                                    'temp_lateness': trans.temp_lateness - perm_time,
                                    }
                        perm_time = 0
                        if state != 'check': trans.update(perm_dic)
                        if state is not None:
                            feedback.append(
                                {'perm_id': perm.id, 'perm_start': perm_start, 'perm_end': perm_end, 'type': 'late'})
                if trans.temp_exit:
                    if perm_df <= sign_out and perm_dt >= shift_out:
                        perm_time = round((shift_out - sign_out).seconds / 60 / 60, 2)
                        perm_start, perm_end = sign_out, shift_out
                    elif perm_df <= sign_out and perm_dt < shift_out and perm_dt > sign_out:
                        perm_time = round((perm_dt - sign_out).seconds / 60 / 60, 2)
                        perm_start, perm_end = sign_out, perm_dt
                    elif perm_df > sign_out and perm_dt >= shift_out and perm_df < shift_out:
                        perm_time = round((shift_out - perm_df).seconds / 60 / 60, 2)
                        perm_start, perm_end = perm_df, shift_out
                    elif perm_df > sign_out and perm_dt < shift_out:
                        perm_time = round((perm_dt - perm_df).seconds / 60 / 60, 2)
                        perm_start, perm_end = perm_df, perm_dt
                    if perm_time:
                        perm_dic = {'approve_personal_permission': True,
                                    'personal_permission_id': perm.id,
                                    'total_permission_hours': perm_time,
                                    'temp_exit': trans.temp_exit - perm_time,
                                    }
                        perm_time = 0
                        if state != 'check': trans.update(perm_dic)
                        if state is not None:
                            feedback.append(
                                {'perm_id': perm.id, 'perm_start': perm_start, 'perm_end': perm_end, 'type': 'exit'})
                if breaks:
                    for brk in breaks:
                        if not (perm_df < perm_dt and brk['break_start'] < brk['break_end']): continue
                        if brk['break_start'] <= perm_df and brk['break_end'] >= perm_dt:
                            perm_time = round((perm_dt - perm_df).seconds / 60 / 60, 2)
                            perm_start, perm_end = perm_df, perm_dt
                        elif brk['break_start'] > perm_df and brk['break_end'] < perm_dt:
                            perm_time = round((brk['break_end'] - brk['break_start']).seconds / 60 / 60, 2)
                            perm_start, perm_end = brk['break_start'], brk['break_end']
                        elif brk['break_start'] <= perm_df and brk['break_end'] < perm_dt and brk[
                            'break_end'] > perm_df:
                            perm_time = round((brk['break_end'] - perm_df).seconds / 60 / 60, 2)
                            perm_start, perm_end = perm_df, brk['break_end']
                        elif brk['break_start'] > perm_df and brk['break_end'] >= perm_dt and brk[
                            'break_start'] < perm_dt:
                            perm_time = round((perm_dt - brk['break_start']).seconds / 60 / 60, 2)
                            perm_start, perm_end = brk['break_start'], perm_dt
                        if perm_time:
                            perm_dic = {'approve_personal_permission': True,
                                        'personal_permission_id': perm.id,
                                        'total_permission_hours': perm_time,
                                        'break_duration': trans.break_duration - perm_time,
                                        }
                            if state != 'check': trans.update(perm_dic)
                            if state is not None:
                                feedback.append(
                                    {'perm_id': perm.id, 'perm_start': perm_start, 'perm_end': perm_end,
                                     'type': 'break'})
                        perm_time = 0
            if state is not None: return feedback

    def manage_mission(self, trans_id, shift_in, shift_out, sign_in, sign_out, breaks, state=None):
        trans, feedback = self.browse(trans_id)[0], []
        if trans.official_id:
            trans.update({'is_official': False, 'official_id': False, 'total_mission_hours': 0.0})
        date_from_time = (shift_in + timedelta(hours=3)).time()
        date_to_time = (shift_out + timedelta(hours=3)).time()
        hour_from = date_from_time.hour + date_from_time.minute / 60.0
        hour_to = date_to_time.hour + date_to_time.minute / 60.0
        missions = self.env['hr.official.mission'].search([('state', '=', 'approve'),
                                                           ('employee_ids.employee_id', 'in',
                                                            [trans.employee_id.id]),
                                                           ('date_from', '<=', str(shift_in.date())),
                                                           ('date_to', '>=', str(shift_in.date())),
                                                           '|', '|',
                                                           '&', ('hour_from', '<=', hour_from),
                                                           ('hour_to', '>=', hour_from),
                                                           '&', ('hour_from', '<=', hour_to),
                                                           ('hour_to', '>=', hour_to),
                                                           '&', ('hour_from', '>=', hour_from),
                                                           ('hour_to', '<=', hour_to),
                                                           ])
        if missions:
            for mission in missions:
                emp_mission = mission.employee_ids.filtered(lambda m: m.employee_id.id == trans.employee_id.id)[0]
                miss_time = 0
                mission_date = datetime.combine(fields.Datetime.from_string(mission.date), datetime.min.time())
                mission_df = self.convert_float_2time(emp_mission.hour_from, mission_date)
                mission_dt = self.convert_float_2time(emp_mission.hour_to, mission_date)
                if trans.sign_in == 0.0 or trans.sign_out == 0.0:
                    miss_dic = {'is_official': True,
                                'official_id': mission.id,
                                'total_mission_hours': mission.hour_duration,
                                }
                    if state != 'check': trans.update(miss_dic)
                    if state is not None:
                        feedback.append(
                            {'mission_id': mission.id, 'miss_start': mission_df, 'miss_end': mission_dt, 'type': 'all'})
                    continue
                if trans.temp_lateness:
                    if mission_df <= shift_in and mission_dt >= sign_in:
                        miss_time = round((sign_in - shift_in).seconds / 60 / 60, 2)
                        miss_start, miss_end = shift_in, sign_in
                    elif mission_df <= shift_in and mission_dt < sign_in and mission_dt > shift_in:
                        miss_time = round((mission_dt - shift_in).seconds / 60 / 60, 2)
                        miss_start, miss_end = shift_in, mission_dt
                    elif (mission_df > shift_in and mission_dt < sign_in) or sign_in == 0.0 or sign_out == 0.0:
                        miss_time = round((mission_dt - mission_df).seconds / 60 / 60, 2)
                        miss_start, miss_end = mission_df, mission_dt
                    elif mission_df < sign_in and mission_df > shift_in and mission_dt >= sign_in:
                        miss_time = round((sign_in - mission_df).seconds / 60 / 60, 2)
                        miss_start, miss_end = mission_df, sign_in
                    if miss_time:
                        miss_dic = {'is_official': True,
                                    'official_id': mission.id,
                                    'total_mission_hours': miss_time,
                                    'temp_lateness': trans.temp_lateness - miss_time,
                                    }
                        miss_time = 0
                        if state != 'check': trans.update(miss_dic)
                        if state is not None:
                            # perm_dic.update({ 'personal_permission_id': perm.id,'perm_start': perm_start, 'perm_end': perm_end})
                            feedback.append(
                                {'mission_id': mission.id, 'miss_start': miss_start, 'miss_end': miss_end,
                                 'type': 'late'})
                if trans.temp_exit:
                    if mission_df <= sign_out and mission_dt >= shift_out:
                        miss_time = round((shift_out - sign_out).seconds / 60 / 60, 2)
                        miss_start, miss_end = sign_out, shift_out
                    elif mission_df <= sign_out and mission_dt < shift_out and mission_dt > sign_out:
                        miss_time = round((mission_dt - sign_out).seconds / 60 / 60, 2)
                        miss_start, miss_end = sign_out, mission_dt
                    elif mission_df > sign_out and mission_dt >= shift_out and mission_df < shift_out:
                        miss_time = round((shift_out - mission_df).seconds / 60 / 60, 2)
                        miss_start, miss_end = mission_df, shift_out
                    elif mission_df > sign_out and mission_dt < shift_out:
                        miss_time = round((mission_dt - mission_df).seconds / 60 / 60, 2)
                        miss_start, miss_end = mission_df, mission_dt
                    if miss_time:
                        miss_dic = {'is_official': True,
                                    'official_id': mission.id,
                                    'total_mission_hours': miss_time,
                                    'temp_exit': trans.temp_exit - miss_time,
                                    }
                        miss_time = 0
                        if state != 'check': trans.update(miss_dic)
                        if state is not None:
                            feedback.append(
                                {'mission_id': mission.id, 'miss_start': miss_start, 'miss_end': miss_end,
                                 'type': 'exit'})
                if breaks:
                    for brk in breaks:
                        if not (mission_df < mission_dt and brk['break_start'] < brk['break_end']): continue
                        if brk['break_start'] <= mission_df and brk['break_end'] >= mission_dt:
                            miss_time = round((mission_dt - mission_df).seconds / 60 / 60, 2)
                            miss_start, miss_end = mission_df, mission_dt
                        elif brk['break_start'] > mission_df and brk['break_end'] < mission_dt:
                            miss_time = round((brk['break_end'] - brk['break_start']).seconds / 60 / 60, 2)
                            miss_start, miss_end = brk['break_start'], brk['break_end']
                        elif brk['break_start'] <= mission_df and brk['break_end'] < mission_dt and brk[
                            'break_end'] > mission_df:
                            miss_time = round((brk['break_end'] - mission_df).seconds / 60 / 60, 2)
                            miss_start, miss_end = mission_df, brk['break_end']
                        elif brk['break_start'] > mission_df and brk['break_end'] >= mission_dt and brk[
                            'break_start'] < mission_dt:
                            miss_time = round((mission_dt - brk['break_start']).seconds / 60 / 60, 2)
                            miss_start, miss_end = brk['break_start'], mission_dt
                        if miss_time:
                            miss_dic = {'is_official': True,
                                        'official_id': mission.id,
                                        'total_mission_hours': miss_time,
                                        'break_duration': trans.break_duration - miss_time,
                                        }
                            if state != 'check': trans.update(miss_dic)
                            if state is not None:
                                feedback.append(
                                    {'mission_id': mission.id, 'miss_start': miss_start, 'miss_end': miss_end,
                                     'type': 'break'})
                        miss_time = 0
            if state is not None: return feedback

    @api.model
    def process_attendance_scheduler_queue(self, attendance_date=None, attendance_employee=None):
        at_device = self.env['ir.module.module'].sudo().search([('state', '=', 'installed'),
                                                                ('name', '=', 'to_attendance_device_custom')]) \
                    and True or False
        attendance_pool = self.env['attendance.attendance']
        low_date = (datetime.utcnow()).date() if not attendance_date else attendance_date
        if isinstance(low_date, datetime):
            low_date = low_date.date()
        if low_date:
            module = self.env['ir.module.module'].sudo()
            official_mission_module = module.search(
                [('state', '=', 'installed'), ('name', '=', 'exp_official_mission')])
            personal_permission_module = module.search(
                [('state', '=', 'installed'), ('name', '=', 'employee_requests')])
            holidays_module = module.search([('state', '=', 'installed'), ('name', '=', 'hr_holidays_public')])
            if holidays_module:
                holiday_pool = self.env['hr.holidays']
            transactions = self.env['hr.attendance.transaction']

            day_item = low_date
            weekday = day_item.strftime('%A').lower()
            prv_day_item = day_item - timedelta(1)
            prv_weekday = prv_day_item.strftime('%A').lower()
            nxt_day_item = day_item + timedelta(1)
            nxt_weekday = nxt_day_item.strftime('%A').lower()
            if holidays_module:
                public = self.env['hr.holiday.officials'].search([('active', '=', True), ('state', '=', 'confirm'),
                                                                  ('date_from', '<=', day_item),
                                                                  ('date_to', '>=', day_item)])
            employee_list = self.env['hr.employee'].search([('state', '=', 'open')]) \
                if not attendance_employee else attendance_employee
            for employee in employee_list:
                hire = employee.contract_id.hiring_date if employee.contract_id.hiring_date else employee.contract_id.date_start
                datetime_object = datetime.strptime(str(hire), '%Y-%m-%d').date()
                if employee.contract_id.state != 'end_contract' and datetime_object <= day_item:
                    if datetime_object == day_item:
                        day_item = datetime_object
                    else:
                        day_item = low_date
                    check_trans = self.search([('date', '=', day_item), ('employee_id', '=', employee.id)])
                    emp_calendar = check_trans and check_trans[0].calendar_id and check_trans[0].calendar_id \
                                   or employee.resource_calendar_id
                    if emp_calendar.is_full_day:
                        attendance_dt = datetime.combine(day_item, datetime.min.time())
                        day_times, planed_hours = self.get_day_timing(emp_calendar, weekday, day_item)
                        one_min_in, one_max_in = day_times[0], day_times[1]
                        one_min_out, one_max_out = day_times[2], day_times[3]
                        one_min_in_dt = self.convert_float_2time(one_min_in, attendance_dt)
                        domain = [('employee_id', '=', employee.id)]
                        if emp_calendar.noke and not self.one_day_noke(emp_calendar):
                            one_max_in_dt = self.noke_time_2date('one_max_in', attendance_dt, day_times)
                            one_min_out_dt = self.noke_time_2date('one_min_out', attendance_dt, day_times)
                            one_max_out_dt = self.noke_time_2date('one_max_out', attendance_dt, day_times)

                            one_max_out_st = fields.Datetime.to_string(one_max_out_dt)
                            domain += [('action_date', 'in', (day_item, day_item + timedelta(1)))]
                            prv_day_times = self.get_day_timing(emp_calendar, prv_weekday, prv_day_item)[0]
                            prv_day_min_out = self.noke_time_2date('one_min_out', attendance_dt - timedelta(1),
                                                                   prv_day_times)
                            prv_day_max_out = self.noke_time_2date('one_max_out', attendance_dt - timedelta(1),
                                                                   prv_day_times)
                            nxt_day_times = self.get_day_timing(emp_calendar, nxt_weekday, nxt_day_item)[0]
                            nxt_day_min_in = self.convert_float_2time(nxt_day_times[0], attendance_dt + timedelta(1))
                            one_in_dom = domain.copy() + [('action', '=', 'sign_in'),
                                                          ('name', '<=', one_max_out_st),
                                                          ('name', '>', str(prv_day_max_out))]
                            out_dom = domain.copy() + [('action', '=', 'sign_out'),
                                                       ('name', '>', str(prv_day_max_out)),
                                                       ('name', '<', str(nxt_day_min_in))]
                        else:
                            one_max_in_dt = self.convert_float_2time(one_max_in, attendance_dt)
                            one_min_out_dt = self.convert_float_2time(one_min_out, attendance_dt)
                            one_max_out_dt = self.convert_float_2time(one_max_out, attendance_dt)
                            one_max_out_st = fields.Datetime.to_string(one_max_out_dt)
                            domain += [('action_date', '=', day_item)]
                            one_in_dom = domain.copy() + [('action', '=', 'sign_in'), ('name', '<=', one_max_out_st)]
                            out_dom = domain.copy() + [('action', '=', 'sign_out')]
                        signs_out = attendance_pool.search(out_dom, order="name asc")
                        one_signs_in = attendance_pool.search(one_in_dom, order="name asc")
                        base_dict = {'date': day_item, 'employee_id': employee.id, 'calendar_id': emp_calendar.id,
                                     'attending_type': 'in_cal'}
                        one_dict, shift_one_extra, force_create = {}, {}, True
                        exist_trans = transactions.search([('date', '=', day_item), ('employee_id', '=', employee.id)])
                        if not (not one_signs_in and not signs_out):
                            if one_signs_in:
                                signs_out = signs_out.filtered(
                                    lambda s: s.name >= str(one_signs_in[0].name)) or attendance_pool
                            one_dict = self.prepare_shift(at_device, attendance_dt, one_signs_in, signs_out, one_min_in_dt,
                                                          one_max_in_dt, one_min_out_dt, one_max_out_dt, base_dict.copy())
                            if one_dict:
                                shift_one = one_dict['shift']
                                shift_one['sequence'] = 1
                                one_breaks = one_dict.get('break_periods', {})
                                one_in_dt, one_out_dt = shift_one['sign_in_dt'], shift_one['sign_out_dt']
                                del shift_one['sign_in_dt']
                                del shift_one['sign_out_dt']
                                if one_out_dt:
                                    signs_out = signs_out.filtered(lambda s: s.name > str(one_out_dt))
                                force_create = False
                                if shift_one.get('attending_type') == 'out_cal':
                                    shift_one_extra = {'sign_in': 0.0, 'sign_out': 0.0, 'date': day_item, 'sequence': 1,
                                                       'employee_id': employee.id, 'calendar_id': emp_calendar.id,
                                                       'attending_type': 'in_cal'}
                        if force_create or not one_dict:
                            shift_one = {'sign_in': 0.0, 'sign_out': 0.0, 'date': day_item, 'employee_id': employee.id,
                                         'is_absent': True, 'calendar_id': emp_calendar.id, 'sequence': 1,
                                         'attending_type': 'in_cal'}
                            one_in_dt, one_out_dt = one_min_in_dt, one_max_out_dt
                            one_breaks = {}
                            force_create = True
                        one_exist_trans = exist_trans and exist_trans.filtered(
                            lambda t: t.sequence == 1 and t.attending_type == shift_one['attending_type']) or False
                        if one_exist_trans:
                            one_exist_trans.update(shift_one)
                            one_trans = one_exist_trans
                        else:
                            one_trans = transactions.create(shift_one)
                        if shift_one_extra:
                            onextra_exist_trans = exist_trans and \
                                                  exist_trans.filtered(
                                                      lambda t: t.sequence == 1 and t.attending_type == 'out_cal') or False
                            if onextra_exist_trans:
                                onextra_exist_trans.update(shift_one_extra)
                            else:
                                transactions.create(shift_one_extra)
                        one_trans = exist_trans and \
                                    exist_trans.filtered(
                                        lambda t: t.sequence == 1 and t.attending_type == 'in_cal') or one_trans
                        one_extra_dlt = exist_trans and \
                                        exist_trans.filtered(
                                            lambda t: t.sequence == 1 and t.attending_type == 'out_cal') or False
                        if one_extra_dlt and not shift_one_extra: one_extra_dlt.unlink()
                        if personal_permission_module:
                            if one_trans.temp_lateness or one_trans.temp_exit or one_breaks \
                                    or one_trans.sign_in == 0.0 or one_trans.sign_out == 0.0:
                                one_perm = self.manage_permission(one_trans.id, one_min_in_dt, one_max_out_dt,
                                                                  one_in_dt, one_out_dt, one_breaks, 'inform')
                        if official_mission_module:
                            self.manage_mission(one_trans.id, one_min_in_dt, one_max_out_dt, one_in_dt, one_out_dt,
                                                one_breaks)
                    else:
                        day_times, planed_hours = self.get_day_timing(emp_calendar, weekday, day_item)
                        one_min_in, one_max_in = day_times[0], day_times[1]
                        one_min_out, one_max_out = day_times[2], day_times[3]
                        two_min_in, two_max_in = day_times[4], day_times[5]
                        two_min_out, two_max_out = day_times[6], day_times[7]
                        attendance_dt = datetime.combine(day_item, datetime.min.time())
                        one_min_in_dt = self.convert_float_2time(one_min_in, attendance_dt)
                        domain = [('employee_id', '=', employee.id)]
                        if emp_calendar.noke and not self.one_day_noke(emp_calendar):
                            one_max_in_dt = self.noke_time_2date('one_max_in', attendance_dt, day_times)
                            one_min_out_dt = self.noke_time_2date('one_min_out', attendance_dt, day_times)
                            one_max_out_dt = self.noke_time_2date('one_max_out', attendance_dt, day_times)
                            two_min_in_dt = self.noke_time_2date('two_min_in', attendance_dt, day_times)
                            two_max_in_dt = self.noke_time_2date('two_max_in', attendance_dt, day_times)
                            two_min_out_dt = self.noke_time_2date('two_min_out', attendance_dt, day_times)
                            two_max_out_dt = self.noke_time_2date('two_max_out', attendance_dt, day_times)
                            one_max_out_st = fields.Datetime.to_string(one_max_out_dt)
                            domain += [('action_date', 'in', (day_item, day_item + timedelta(1)))]
                            prv_day_times = self.get_day_timing(emp_calendar, prv_weekday, prv_day_item)[0]
                            prv_day_min_out = self.noke_time_2date('two_min_out', attendance_dt - timedelta(1),
                                                                   prv_day_times)
                            prv_day_max_out = self.noke_time_2date('two_max_out', attendance_dt - timedelta(1),
                                                                   prv_day_times)
                            nxt_day_times = self.get_day_timing(emp_calendar, nxt_weekday, nxt_day_item)[0]
                            nxt_day_min_in = self.convert_float_2time(nxt_day_times[0], attendance_dt + timedelta(1))
                            one_in_dom = domain.copy() + [('action', '=', 'sign_in'),
                                                          ('name', '<=', one_max_out_st),
                                                          ('name', '>', str(prv_day_min_out))]
                            two_in_dom = domain.copy() + [('action', '=', 'sign_in'),
                                                          ('name', '>', one_max_out_st),
                                                          ('name', '<=', str(two_min_out_dt))]
                            out_dom = domain.copy() + [('action', '=', 'sign_out'),
                                                       ('name', '>', str(prv_day_max_out)),
                                                       ('name', '<', str(nxt_day_min_in))]
                        else:
                            one_max_in_dt = self.convert_float_2time(one_max_in, attendance_dt)
                            one_min_out_dt = self.convert_float_2time(one_min_out, attendance_dt)
                            one_max_out_dt = self.convert_float_2time(one_max_out, attendance_dt)
                            two_min_in_dt = self.convert_float_2time(two_min_in, attendance_dt)
                            two_max_in_dt = self.convert_float_2time(two_max_in, attendance_dt)
                            two_min_out_dt = self.convert_float_2time(two_min_out, attendance_dt)
                            two_max_out_dt = self.convert_float_2time(two_max_out, attendance_dt)
                            one_max_out_st = fields.Datetime.to_string(one_max_out_dt)
                            domain += [('action_date', '=', day_item)]
                            one_in_dom = domain.copy() + [('action', '=', 'sign_in'), ('name', '<', one_max_out_st)]
                            two_in_dom = domain.copy() + [('action', '=', 'sign_in'), ('name', '>=', one_max_out_st)]
                            out_dom = domain.copy() + [('action', '=', 'sign_out')]
                        signs_out = attendance_pool.search(out_dom, order="name asc")
                        one_signs_in = attendance_pool.search(one_in_dom, order="name asc")
                        two_signs_in = attendance_pool.search(two_in_dom, order="name asc")
                        base_dict = {'date': day_item, 'employee_id': employee.id, 'calendar_id': emp_calendar.id,
                                     'attending_type': 'in_cal'}
                        one_dict, two_dict, shift_one_extra, shift_two_extra, force_create = {}, {}, {}, {}, True
                        exist_trans = transactions.search([('date', '=', day_item), ('employee_id', '=', employee.id)])
                        if not (not one_signs_in and not signs_out):
                            if one_signs_in:
                                signs_out = signs_out.filtered(
                                    lambda s: s.name > str(one_signs_in[0].name)) or attendance_pool
                            one_dict = self.prepare_shift(at_device, attendance_dt, one_signs_in, signs_out, one_min_in_dt,
                                                          one_max_in_dt, one_min_out_dt, one_max_out_dt, base_dict.copy(),
                                                          two_min_in_dt)
                            if one_dict:
                                shift_one = one_dict['shift']
                                shift_one['sequence'] = 1
                                one_breaks = one_dict.get('break_periods', {})
                                one_in_dt, one_out_dt = shift_one['sign_in_dt'], shift_one['sign_out_dt']
                                del shift_one['sign_in_dt']
                                del shift_one['sign_out_dt']
                                if one_out_dt: signs_out = signs_out.filtered(lambda s: s.name > str(one_out_dt))
                                force_create = False
                                if shift_one.get('attending_type') == 'out_cal':
                                    shift_one_extra = {'sign_in': 0.0, 'sign_out': 0.0, 'date': day_item, 'sequence': 1,
                                                       'employee_id': employee.id, 'calendar_id': emp_calendar.id,
                                                       'attending_type': 'in_cal'}
                        if force_create or not one_dict:
                            shift_one = {'sign_in': 0.0, 'sign_out': 0.0, 'date': day_item, 'employee_id': employee.id,
                                         'is_absent': True, 'calendar_id': emp_calendar.id, 'sequence': 1,
                                         'attending_type': 'in_cal'}
                            one_in_dt, one_out_dt = one_min_in_dt, one_max_out_dt
                            one_breaks = {}
                            force_create = True
                        if not (not two_signs_in and not signs_out):
                            two_dict = self.prepare_shift(at_device, attendance_dt, two_signs_in, signs_out, two_min_in_dt,
                                                          two_max_in_dt, two_min_out_dt, two_max_out_dt, base_dict)
                            if two_signs_in:
                                signs_out = signs_out.filtered(
                                    lambda s: s.name > str(two_signs_in[0].name)) or attendance_pool
                            if two_dict:
                                shift_two = two_dict['shift']
                                shift_two['sequence'] = 2
                                two_breaks = two_dict.get('break_periods', {})
                                two_in_dt, two_out_dt = shift_two['sign_in_dt'], shift_two['sign_out_dt']
                                del shift_two['sign_in_dt']
                                del shift_two['sign_out_dt']
                                force_create = False
                                if shift_two.get('attending_type') == 'out_cal':
                                    shift_two_extra = {'sign_in': 0.0, 'sign_out': 0.0, 'date': day_item, 'sequence': 2,
                                                       'employee_id': employee.id, 'calendar_id': emp_calendar.id,
                                                       'attending_type': 'in_cal'}
                        if force_create or not two_dict:
                            shift_two = {'sign_in': 0.0, 'sign_out': 0.0, 'date': day_item, 'employee_id': employee.id,
                                         'calendar_id': emp_calendar.id, 'sequence': 2, 'attending_type': 'in_cal'}
                            two_in_dt, two_out_dt = two_min_in_dt, two_max_out_dt
                            two_breaks = {}
                            force_create = True
                        if one_dict and one_dict['creep']:
                            # TODO: review cases not to be minus
                            shift_one['official_hours'] += one_dict['creep']
                            if two_dict and shift_two['temp_lateness'] and shift_two.get('attending_type') == 'in_cal':
                                shift_two['break_duration'] += shift_two['temp_lateness'] - one_dict['creep']
                                # shift_two['temp_lateness'] = 0.0
                                shift_two['carried_hours'] = one_dict['creep']
                        one_exist_trans = exist_trans and exist_trans.filtered(
                            lambda t: t.sequence == 1 and t.attending_type == shift_one['attending_type']) or False
                        if one_exist_trans:
                            one_exist_trans.update(shift_one)
                            one_trans = one_exist_trans
                        else:
                            one_trans = transactions.create(shift_one)
                        two_exist_trans = exist_trans and exist_trans.filtered(
                            lambda t: t.sequence == 2 and t.attending_type == shift_two['attending_type']) or False
                        if two_exist_trans:
                            two_exist_trans.update(shift_two)
                            two_trans = two_exist_trans
                        else:
                            two_trans = transactions.create(shift_two)
                        if shift_one_extra:
                            onextra_exist_trans = exist_trans and \
                                                  exist_trans.filtered(
                                                      lambda t: t.sequence == 1 and t.attending_type == 'out_cal') or False
                            if onextra_exist_trans:
                                onextra_exist_trans.update(shift_one_extra)
                            else:
                                transactions.create(shift_one_extra)
                        if shift_two_extra:
                            twoxtra_exist_trans = exist_trans and \
                                                  exist_trans.filtered(
                                                      lambda t: t.sequence == 2 and t.attending_type == 'in_cal') or False
                            if twoxtra_exist_trans:
                                twoxtra_exist_trans.update(shift_two_extra)
                            else:
                                transactions.create(shift_two_extra)
                        one_trans = exist_trans and \
                                    exist_trans.filtered(
                                        lambda t: t.sequence == 1 and t.attending_type == 'in_cal') or one_trans
                        one_extra_dlt = exist_trans and \
                                        exist_trans.filtered(
                                            lambda t: t.sequence == 1 and t.attending_type == 'out_cal') or False
                        if one_extra_dlt and not shift_one_extra: one_extra_dlt.unlink()
                        two_trans = exist_trans and \
                                    exist_trans.filtered(
                                        lambda t: t.sequence == 2 and t.attending_type == 'in_cal') or two_trans
                        two_extra_dlt = exist_trans and \
                                        exist_trans.filtered(
                                            lambda t: t.sequence == 2 and t.attending_type == 'out_cal') or False
                        if two_extra_dlt and not shift_two_extra: two_extra_dlt.unlink()
                        if personal_permission_module:
                            if one_trans.temp_lateness or one_trans.temp_exit or one_breaks \
                                    or one_trans.sign_in == 0.0 or one_trans.sign_out == 0.0:
                                one_perm = self.manage_permission(one_trans.id, one_min_in_dt, one_max_out_dt,
                                                                  one_in_dt, one_out_dt, one_breaks, 'inform')
                            if two_trans.temp_lateness or two_trans.temp_exit or two_breaks \
                                    or two_trans.sign_in == 0.0 or two_trans.sign_out == 0.0:
                                two_perm = self.manage_permission(two_trans.id, two_min_in_dt, two_max_out_dt,
                                                                  two_in_dt, two_out_dt, two_breaks, 'inform')
                        if official_mission_module:
                            self.manage_mission(one_trans.id, one_min_in_dt, one_max_out_dt, one_in_dt, one_out_dt,
                                                one_breaks)
                            self.manage_mission(two_trans.id, two_min_in_dt, two_max_out_dt, two_in_dt, two_out_dt,
                                                two_breaks)

                    off_list = []
                    day_trans = transactions.search([('date', '=', day_item), ('employee_id', '=', employee.id)])
                    weekend_days = emp_calendar.is_full_day and emp_calendar.full_day_off or emp_calendar.shift_day_off
                    if weekend_days:
                        for day in weekend_days:
                            create = (datetime.strptime(str(day.create_date.strftime(DATETIME_FORMAT)),
                                                        DATETIME_FORMAT) + timedelta(hours=3)).date()
                            off_list.append(day.name.lower())
                            if day.name.lower() == day_item.strftime('%A').lower():
                                for trans in day_trans:
                                    if emp_calendar.noke and create <= datetime.strptime(trans.date, "%Y-%m-%d").date():
                                        trans.update({'public_holiday': True})
                                    else:
                                        trans.update({'public_holiday': True})
                            else:
                                for trans in day_trans:
                                    if trans.public_holiday and not trans.public_holiday_id:
                                        trans_wkd = datetime.strptime(str(trans.date), "%Y-%m-%d")
                                        if trans_wkd.strftime('%A').lower() not in off_list and not trans.public_holiday_id:
                                            if emp_calendar.noke:
                                                pass
                                            else:
                                                trans.update({'public_holiday': False})
                    else:
                        for trans in day_trans:
                            if trans.public_holiday and not trans.public_holiday_id:
                                if emp_calendar.noke:
                                    pass
                                else:
                                    trans.update({'public_holiday': False})
                    if holidays_module:
                        ptrans = transactions.search([('date', '=', day_item), ('employee_id', '=', employee.id)])
                        public_trans = ptrans.filtered(lambda pk: pk.public_holiday_id)
                        if public:
                            for p in public:
                                for trans in ptrans:
                                    if p.date_from <= trans.date and p.date_to >= trans.date:
                                        trans.update({'public_holiday': True, 'public_holiday_id': p.id})
                        elif public_trans and not public:
                            for trans in public_trans:
                                if trans.public_holiday:
                                    trans.update({'public_holiday': False, 'public_holiday_id': False})
                        emp_stateless_leaves = holiday_pool.search([('employee_id', '=', employee.id),
                                                                    ('type', '!=', 'add'),
                                                                    ('date_from', '<=', str(day_item)),
                                                                    ('date_to', '>=', str(day_item))])
                        leaves = emp_stateless_leaves.filtered(lambda l: l.state == 'validate1')
                        cancelled_leaves = emp_stateless_leaves.filtered(lambda l: l.state != 'validate1')
                        if leaves:
                            for lev in leaves:
                                if lev.date_from and lev.date_to \
                                        and fields.Date.from_string(lev.date_from).strftime('%Y-%m-%d') \
                                        <= str(day_item) <= str(lev.date_to):
                                    for trans in ptrans:
                                        lv_hours = trans.calendar_id.is_full_day and trans.calendar_id.working_hours \
                                                   or trans.sequence == 1 and trans.calendar_id.shift_one_working_hours \
                                                   or trans.sequence == 2 and trans.calendar_id.shift_two_working_hours
                                        trans.update({
                                            'normal_leave': True,
                                            'leave_id': lev.id,
                                            'total_leave_hours': lv_hours,
                                            'break_duration': 0.0,
                                            'public_holiday': False,
                                            'is_absent': False,
                                            'total_absent_hours': 0.0})
                        elif cancelled_leaves:
                            for trans in ptrans:
                                for lev in cancelled_leaves:
                                    if lev.id == trans.leave_id.id:
                                        trans.update({'normal_leave': False, 'leave_id': False, 'total_leave_hours': 0.0})
                    for tr in day_trans:
                        if tr.attending_type == 'in_cal':
                            if tr.sequence == 1:
                                tr.plan_hours = planed_hours['one']
                            elif tr.sequence == 2:
                                tr.plan_hours = planed_hours['two']

                    # for employee in employee_list:
                    #     emp_tr = day_trans.filtered(lambda t: t.employee_id == employee)
                    #     template = self.env.ref('attendences.email_template_transaction_state')
                    #     if len(day_trans.filtered(lambda t: t.employee_id == employee)) == 1:
                    #         if emp_tr.is_absent:
                    #             msg = "is absent"
                    #             body = """<div>
                    #             <p>Dear %s ,</p>
                    #             <p> Greetings, we kindly inform you that employee %s %s on %s
                    #             <br/>
                    #             <p>Best regards,</p>
                    #              """ % (employee.parent_id.name, employee.name, msg, emp_tr.date)
                    #             template.write({'body_html': body})
                    #             template.send_mail(emp_tr.id, force_send=True, raise_exception=False)
                    #         if emp_tr.approve_lateness:
                    #             msg = "is late"
                    #             body = """<div>
                    #             <p>Dear %s ,</p>
                    #             <p> Greetings, we kindly inform you that employee %s %s on %s
                    #             <br/>
                    #              <p>Best regards,</p>
                    #              """ % (employee.parent_id.name, employee.name, msg, emp_tr.date)
                    #             template.write({'body_html': body})
                    #             template.send_mail(emp_tr.id, force_send=True, raise_exception=False)
                    #         if emp_tr.approve_exit_out:
                    #             msg = "is exit out"
                    #             body = """<div>
                    #             <p>Dear %s ,</p>
                    #             <p> Greetings, we kindly inform you that employee %s %s on %s
                    #             <br/>
                    #             <p>Best regards,</p>
                    #              """ % (employee.parent_id.name, employee.name, msg, emp_tr.date)
                    #             template.write({'body_html': body})
                    #             template.send_mail(emp_tr.id, force_send=True, raise_exception=False)
                    #     else:
                    #         if all(tr.is_absent for tr in emp_tr):
                    #             if emp_tr and emp_tr[0]:
                    #                 msg = "is absent"
                    #                 body = """<div>
                    #                 <p>Dear %s ,</p>
                    #                 <p> Greetings, we kindly inform you that employee %s %s on %s
                    #                 <br/>
                    #                 <p>Best regards,</p>
                    #                 """ % (employee.parent_id.name, employee.name, msg, emp_tr[0].date)
                    #                 template.write({'body_html': body})
                    #                 template.send_mail(emp_tr[0].id, force_send=True, raise_exception=False)
                    #         if all(tr.approve_lateness for tr in emp_tr):
                    #             if emp_tr and emp_tr[0]:
                    #                 msg = "is later"
                    #                 body = """<div>
                    #                 <p>Dear %s ,</p>
                    #                 <p> Greetings, we kindly inform you that employee %s %s on %s
                    #                 <br/>
                    #                 <p>Best regards,</p>
                    #                 """ % (employee.parent_id.name, employee.name, msg, emp_tr[0].date)
                    #                 template.write({'body_html': body})
                    #                 template.send_mail(emp_tr[0].id, force_send=True, raise_exception=False)
                    #         if all(tr.approve_exit_out for tr in emp_tr):
                    #             if emp_tr and emp_tr[0]:
                    #                 msg = "is exit out"
                    #                 body = """<div>
                    #                 <p>Dear %s ,</p>
                    #                 <p> Greetings, we kindly inform you that employee %s %s on  %s
                    #                 <br/>
                    #                 <p>Best regards,</p>
                    #                 """ % (employee.parent_id.name, employee.name, msg, emp_tr[0].date)
                    #                 template.write({'body_html': body})
                    #                 template.send_mail(emp_tr[0].id, force_send=True, raise_exception=False)

    def get_user_id(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if employee_id:
            return employee_id.id
        else:
            return False

    # @api.multi
    # def unlink(self):
    #     raise UserError(_('Sorry, you can not delete an attendance transaction manually.'))
    #     return super(HrAttendanceTransactions, self).unlink()
