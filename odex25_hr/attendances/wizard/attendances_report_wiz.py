# -*- coding: utf-8 -*-

import collections
import datetime
from odoo import api, fields, models, _


class AttendancesReport(models.TransientModel):
    _name = "employee.attendance.report"
    _description = "Employee Attendance Report"

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    employee_ids = fields.Many2many(comodel_name='hr.employee', string='Employees')
    resource_calender_id = fields.Many2one(comodel_name='resource.calendar', string='Employee work record')
    type = fields.Selection(selection=[('late', 'Late and Early exit'), ('absent', 'Absent'), ('employee', 'Employee')],
                            required=True,
                            default='late', string='Type')

    def print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'resource_calender_id': self.resource_calender_id.id,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'employee_ids': self.employee_ids.ids,
                'type': self.type,
            },
        }
        return self.env.ref('attendances.general_attendance_action_report').report_action(self, data=data)

    def print_excel_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'resource_calender_id': self.resource_calender_id.id,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'employee_ids': self.employee_ids.ids,
                'type': self.type,
            },
        }
        return self.env.ref('attendances.general_attendance_action_xls').report_action(self, data=data, config=False)


class ReportAttendancePublic(models.AbstractModel):
    _name = 'report.attendances.general_attendances_report_temp'
    _description = "General Attendances Report"

    def get_value(self, data):
        type = data['form']['type']
        employee_ids = data['form']['employee_ids']
        resource_calender_id = data['form']['resource_calender_id']
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        domain = [('date', '>=', from_date), ('date', '<=', to_date)]
        data = []
        final_dic = {}
        key_list = []
        total_dic = {}
        mykey = []
        resource = self.env['resource.calendar'].browse(resource_calender_id)
        if resource:
            if resource.employee_ids:
                for emp in resource.employee_ids:
                    employee_ids.append(emp.id)
        # if resource_calender_id:
        #     contract_ids = self.env['hr.contract'].search([('state', '=', 'program_directory'), ('resource_calendar_id', '=', resource_calender_id)])
        #     for con in contract_ids:
        #         employee_ids.append(con.employee_id.id)
        # print(">>>>>>>>>>>>>>>>>>>>>>>employeesemployees",employees)
        if employee_ids:
            last_employee_ids = list(set(employee_ids))
            domain.append(('employee_id', 'in', last_employee_ids))
        attendance_transaction_ids = self.env['hr.attendance.transaction'].search(domain)
        employees = attendance_transaction_ids.mapped('employee_id.name')
        if type == 'late':
            for resource in attendance_transaction_ids:
                data.append({
                    'date': resource.date,
                    'sig_in': resource.sign_in,
                    'sig_out': resource.sign_out,
                    'lateness': resource.lateness,
                    'early_exit': resource.early_exit,
                    'employee_id': resource.employee_id,
                    'employee_name': resource.employee_id.name,
                })
            for emp in employees:
                list_cat = attendance_transaction_ids.filtered(lambda r: r.employee_id.name == emp)
                total_lateness = sum(list_cat.mapped('lateness'))
                total_lateness = str(datetime.timedelta(minutes=total_lateness))
                total_early_exit = sum(list_cat.mapped('early_exit'))
                total_early_exit = str(datetime.timedelta(minutes=total_early_exit))
                list_absent = attendance_transaction_ids.filtered(
                    lambda r: r.employee_id.name == emp and r.is_absent == True)
                total_absent = len(list_absent)
                list_not_log_in = attendance_transaction_ids.filtered(
                    lambda r: r.employee_id.name == emp and r.sign_in == 0.0)
                total_not_sig_in = len(list_not_log_in)
                list_not_log_out = attendance_transaction_ids.filtered(
                    lambda r: r.employee_id.name == emp and r.sign_out == 0.0)
                total_not_sig_out = len(list_not_log_out)
                total_dic[emp] = {'total_lateness': total_lateness, 'total_early_exit': total_early_exit,
                                  'total_absent': total_absent, 'total_not_sig_in': total_not_sig_in,
                                  'total_not_sig_out': total_not_sig_out}
            grouped = collections.defaultdict(list)
            for item in data:
                grouped[item['employee_name']].append(item)
            for key, value in grouped.items():
                final_dic[key] = list(value)
                key_list.append(key)
            mykey = list(dict.fromkeys(key_list))
            return final_dic, mykey, total_dic
        elif type == 'absent':
            for resource in attendance_transaction_ids.filtered(lambda r: r.is_absent == True):
                data.append({
                    'date': resource.date,
                    'employee_name': resource.employee_id.name,
                    'employee_id_department_id_name': resource.employee_id.department_id.name,
                    'day': datetime.datetime.strptime(str(resource.date), '%Y-%m-%d').date().strftime('%A'),
                })
                grouped = collections.defaultdict(list)
                for item in data:
                    grouped[item['employee_id_department_id_name']].append(item)
                for key, value in grouped.items():
                    final_dic[key] = list(value)
                    key_list.append(key)
                mykey = list(dict.fromkeys(key_list))
            return final_dic, mykey, ''
        elif type == 'employee':
            for emp in employees:
                list_cat = attendance_transaction_ids.filtered(lambda r: r.employee_id.name == emp)
                total_lateness = sum(list_cat.mapped('lateness'))
                total_lateness = str(datetime.timedelta(minutes=total_lateness))
                total_early_exit = sum(list_cat.mapped('early_exit'))
                total_early_exit = str(datetime.timedelta(minutes=total_early_exit))
                total_dic[emp] = {'total_lateness': total_lateness, 'total_early_exit': total_early_exit}
                key_list.append(emp)
            mykey = list(dict.fromkeys(key_list))
            return '', mykey, total_dic

    @api.model
    def _get_report_values(self, docids, data=None):
        final_dic, mykey, total = self.get_value(data)
        start_date = data['form']['from_date']
        end_date = data['form']['to_date']
        type = data['form']['type']
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': start_date,
            'date_end': end_date,
            'type': type,
            'data': final_dic,
            'mykey': mykey,
            'total': total,
        }


class AttendancesReportXls(models.AbstractModel):
    _name = 'report.attendances.general_attendance_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, datas):
        x = self.env['report.attendances.general_attendances_report_temp']
        final_dic, mykey, total = ReportAttendancePublic.get_value(x, data)
        start_date = data['form']['from_date']
        end_date = data['form']['to_date']
        type = data['form']['type']
        sheet = workbook.add_worksheet(U'Holiday Report')
        sheet.right_to_left()
        format2 = workbook.add_format(
            {'font_size': 10, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
             'bold': True})
        format2.set_align('center')
        format2.set_align('vcenter')
        if type == 'late':
            sheet.merge_range('C3:G3', _("Late and Early Exit Report"), format2)
            sheet.merge_range('B4:C4', _("From date"), format2)
            sheet.merge_range('F4:G4', _("To date"), format2)
            sheet.write(3, 3, str(start_date)[0:10], format2)
            sheet.write(3, 7, str(end_date)[0:10], format2)
            row = 8
            for key in mykey:
                n = 1
                size = len(final_dic[key])
                tot_size = len(total[key])
                sheet.write(row - 2, n, _('Name'), format2)
                sheet.write(row, n, _('date'), format2)
                sheet.write(row, n + 1, _('Sign in'), format2)
                sheet.write(row, n + 2, _('Sign out'), format2)
                sheet.write(row, n + 3, _('lateness'), format2)
                sheet.write(row, n + 4, _('Early Exit'), format2)
                sheet.write(row, n + 5, _('Notes'), format2)
                data_row = row + 1
                for line in final_dic[key]:
                    sheet.write(row - 2, n + 1, line['employee_name'], format2)
                    sheet.write(data_row, n, line['date'], format2)
                    sheet.write(data_row, n + 1, '{0:02.0f}:{1:02.0f}'.format(*divmod(float(line['sig_in']) * 60, 60)),
                                format2)
                    sheet.write(data_row, n + 2, '{0:02.0f}:{1:02.0f}'.format(*divmod(float(line['sig_out']) * 60, 60)),
                                format2)
                    sheet.write(data_row, n + 3,
                                '{0:02.0f}:{1:02.0f}'.format(*divmod(float(line['lateness']) * 60, 60)), format2)
                    sheet.write(data_row, n + 4,
                                '{0:02.0f}:{1:02.0f}'.format(*divmod(float(line['early_exit']) * 60, 60)), format2)
                    sheet.write(data_row, n + 5, (' '), format2)
                    data_row += 1
                sheet.write(data_row, n, _('Total lateness'), format2)
                sheet.write(data_row, n + 1, str(total[key]['total_lateness']), format2)
                sheet.write(data_row, n + 2, _('Total Early Exit'), format2)
                sheet.write(data_row, n + 3, str(total[key]['total_early_exit']), format2)
                sheet.write(data_row, n + 4, _('Total Absent'), format2)
                sheet.write(data_row, n + 5, str(total[key]['total_absent']), format2)
                size -= 2
                sheet.write(data_row + 1, n, _('Total Not Sign In'), format2)
                sheet.write(data_row + 1, n + 1, str(total[key]['total_not_sig_in']), format2)
                sheet.write(data_row + 1, n + 2, _('Total Not Sign Out'), format2)
                sheet.write(data_row + 1, n + 3, total[key]['total_not_sig_out'], format2)
                n += 1
                row += size + 3 + tot_size
        elif type == 'absent':
            sheet.merge_range('C3:G3', _("Absent Report"), format2)
            sheet.merge_range('C4:G4', _("All Employee - Details"), format2)
            sheet.merge_range('B5:C5', _("From date"), format2)
            sheet.merge_range('F5:G5', _("To date"), format2)
            sheet.write(4, 3, str(start_date)[0:10], format2)
            sheet.write(4, 7, str(end_date)[0:10], format2)
            row = 8
            for key in mykey:
                n = 1
                size = len(final_dic[key])
                sheet.write(row - 2, n, _('Department'), format2)
                sheet.write(row, n, _('Employee Name'), format2)
                sheet.write(row, n + 1, _('Day'), format2)
                sheet.write(row, n + 2, _('date'), format2)
                sheet.write(row, n + 3, _('Notes'), format2)
                data_row = row + 1
                for line in final_dic[key]:
                    sheet.write(row - 2, n + 1, line['employee_id_department_id_name'], format2)
                    sheet.write(data_row, n, line['employee_name'], format2)
                    sheet.write(data_row, n + 1, line['day'], format2)
                    sheet.write(data_row, n + 2, line['date'], format2)
                    sheet.write(data_row, n + 3, (' '), format2)
                    data_row += 1
                n += 1
                row += size + 3
        elif type == 'employee':
            sheet.merge_range('C3:G3', _("Employee Attendance Report"), format2)
            sheet.merge_range('B4:C4', _("From date"), format2)
            sheet.merge_range('F4:G4', _("To date"), format2)
            sheet.write(3, 3, str(start_date)[0:10], format2)
            sheet.write(3, 7, str(end_date)[0:10], format2)
            row = 8
            for key in mykey:
                n = 1
                size = len(total[key])
                sheet.write(row, n, _('Employee Name'), format2)
                sheet.write(row, n + 1, _('Total of Lateness '), format2)
                sheet.write(row, n + 2, _('Total of Early Exit'), format2)
                data_row = row + 1
                sheet.write(data_row, n, key, format2)
                sheet.write(data_row, n + 1, total[key]['total_lateness'], format2)
                sheet.write(data_row, n + 2, total[key]['total_early_exit'], format2)
                data_row += 1
                n += 1
                row += size + 1
