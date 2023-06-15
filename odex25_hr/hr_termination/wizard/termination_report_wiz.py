# -*- coding: utf-8 -*-

import collections
import datetime
from datetime import date
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo import exceptions


class TreminationReport(models.TransientModel):
    _name = "employee.termination.report"
    _description = "Employee Termination Report"

    employee_ids = fields.Many2many(comodel_name='hr.employee', string='Employees', domain="[('state','=','open')]")
    cause_type = fields.Many2one(comodel_name='hr.termination.type')
    salary_date_from = fields.Date()
    salary_date_to = fields.Date()
    end_date = fields.Date(string='End Of Service')
    allowance_ids = fields.Many2many('hr.salary.rule', domain=[('rules_type', 'in', ['house', 'salary', 'transport'])])
    type = fields.Selection(selection=[('salary', 'Salary'), ('ticket', 'Ticket'), ('leave', 'Leave'),
                                       ('termination', 'Termination'), ('all', 'All')], required=True,
                            default='all', string='Type')

    def print_report(self):
        for emp in self.employee_ids:
            if not emp.first_hiring_date:
                raise exceptions.Warning(_('Please set the First Hiring Date %s')
                                         % emp.name)
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'allowance_ids': self.allowance_ids.ids,
                'cause_type': self.cause_type.id,
                'employee_ids': self.employee_ids.ids,
                'type': self.type,
                'date_from': self.salary_date_from,
                'date_to': self.salary_date_to,
                'end_date': self.end_date,
            },
        }
        return self.env.ref('hr_termination.termination_benefits_action_report').report_action(self, data=data)

    def print_excel_report(self):
        for emp in self.employee_ids:
            if not emp.first_hiring_date:
                raise exceptions.Warning(_('Please set the First Hiring Date %s')
                % (emp.name))
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'allowance_ids': self.allowance_ids.ids,
                'cause_type': self.cause_type.id,
                'employee_ids': self.employee_ids.ids,
                'type': self.type,
                'date_from': self.salary_date_from,
                'date_to': self.salary_date_to,
                'end_date': self.end_date,
            },
        }
        return self.env.ref('hr_termination.termination_benefits_xls').report_action(self, data=data, config=False)


class ReportTerminationPublic(models.AbstractModel):
    _name = 'report.hr_termination.termination_report_temp'

    def get_cause_amount(self, first_hire_date, cause_type_name, end_date, emp):
        # Get salary rule  form cause type
        if first_hire_date:
            cause_type_amount = 0.0
            five_year_benefit = 0
            amount = 0
            termination_model = self.env['hr.termination']
            if cause_type_name:
                start_date = datetime.datetime.strptime(str(first_hire_date), "%Y-%m-%d")
                end_date = datetime.datetime.strptime(str(end_date), "%Y-%m-%d")
                total_rules, amount_of_year, amount_of_month, amount_of_day, cause_type_amount = 0.0, 0.0, 0.0, 0.0, 0.0
                five_year_benefit, amount = 0, 0

                if end_date >= start_date:
                    value = relativedelta.relativedelta(end_date, start_date)
                    years = value.years
                    days = value.days
                    months = value.months
                    all_duration = months + (days / 30) + (years * 12)

                    if cause_type_name.allowance_ids and cause_type_name.termination_duration_ids:

                        # Get total for  all salary rules form cause type
                        for rule in cause_type_name.allowance_ids:
                            rule_flag = False
                            if rule_flag is False:
                                total_rules += termination_model.compute_rule(rule, emp.contract_id)
                        for end in cause_type_name.termination_duration_ids:
                            if all_duration >= 24:
                                if end.date_from <= 24 and end.date_to >= 60:
                                    total_rules_year = total_rules * end.factor * end.amount
                                    total_rules_month = total_rules_year / 12
                                    total_rules_day = total_rules_month / 30
                                    if years >= 1:
                                        amount_of_year = total_rules_year * years
                                    if months >= 1:
                                        amount_of_month = total_rules_month * months
                                    if days >= 1:
                                        amount_of_day = total_rules_day * days
                                five_year_benefit = amount_of_year + amount_of_month + amount_of_day
                        for line in cause_type_name.termination_duration_ids:
                            if line.date_from < all_duration and line.date_to >= all_duration:
                                total_rules_year = total_rules * line.factor * line.amount
                                total_rules_month = total_rules_year / 12
                                total_rules_day = total_rules_month / 30
                                if years >= 1:
                                    amount_of_year = total_rules_year * years
                                if months >= 1:
                                    amount_of_month = total_rules_month * months
                                if days >= 1:
                                    amount_of_day = total_rules_day * days
                            cause_type_amount = amount_of_year + amount_of_month + amount_of_day
                            amount = cause_type_amount - five_year_benefit
            return cause_type_amount, five_year_benefit, amount
        else:
            return 0.0
    def get_duration_service(self, first_hire_date, end_date):
        if first_hire_date:
            start_date = datetime.datetime.strptime(str(first_hire_date), "%Y-%m-%d")
            end_date = datetime.datetime.strptime(str(end_date), "%Y-%m-%d")
            if end_date > start_date:
                r = relativedelta.relativedelta(end_date, start_date)
                years = r.years
                months = r.months
                days = r.days
                return years, months, days
            else:
                raise exceptions.Warning(_('Leaving Date  must be greater than First Hiring Date'))

    def get_value(self, data):
        type = data['form']['type']
        employee_ids = data['form']['employee_ids']
        cause_type_id = data['form']['cause_type']
        cause_type_name = self.env['hr.termination.type'].search([('id', '=', cause_type_id)])
        allowance_ids = data['form']['allowance_ids']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        end_date = data['form']['end_date']
        termination_model = self.env['hr.termination']
        data = {'total_rule': {}, 'total_sum': {}}
        key_list = []
        employee_ids = self.env['hr.employee'].search([('id', 'in', employee_ids)])
        rules_ids = self.env['hr.salary.rule'].search([('id', 'in', allowance_ids)])
        if not employee_ids:
          raise exceptions.Warning(_('Sorry, Not Select Employees'))
        for emp in employee_ids:
            total = 0.0
            ticket_num = 0
            ticket_price = 0.0
            cause_amount = 0.0
            five_cause_amount = 0
            amount = 0
            number_year = '0:0:0'
            if emp.first_hiring_date:
                year, month, day = self.get_duration_service(emp.first_hiring_date, end_date)
            if type == 'all' or type == 'termination':
                cause_amount, five_cause_amount, amount = self.get_cause_amount(emp.first_hiring_date, cause_type_name,
                                                                                end_date, emp)
            if type == 'all' or type == 'ticket':
                ticket = self.env['hr.ticket.request'].search([('employee_id', '=', emp.id), ('state', '=', 'done')])
                # if emp.first_hiring_date:
                if ticket:
                    if len(ticket) != year:
                        if len(ticket) < year:
                            ticket_num = year - len(ticket)
                            ticket_price = ticket_num * emp.contract_id.ticket_allowance
                    else:
                        ticket_num = 0
                else:
                    if year < 2:
                        ticket_num = year
                        ticket_price = ticket_num * emp.contract_id.ticket_allowance
                    else:
                        ticket_num = 2
                        ticket_price = ticket_num * emp.contract_id.ticket_allowance
            number_year = ' سنه %s : شهر%s : يوم%s' % (year, month, day)
            salary = 0.0
            data[emp.name] = {
                'date': emp.first_hiring_date,
                'termination_reson': cause_type_name.name,
                'remind_leave_day': emp.remaining_leaves,
                'experiences_year': number_year,
                'ticket': ticket_num,
                'ticket_price': ticket_price,
                'leave_price': '',
                'termination_price': cause_amount,
                'five_year_price': five_cause_amount,
                'amount': amount,
                'total': '',
                'total_salary': 0.0,
                'rule': '',
                'employee_name': emp.name,

            }
            if type == 'all' or type == 'leave':
                if 'remaining_leaves' not in data['total_sum']:
                    data['total_sum']['remaining_leaves'] = emp.remaining_leaves
                else:
                    data['total_sum']['remaining_leaves'] += emp.remaining_leaves
            if type == 'all' or type == 'ticket':
                if 'ticket_num' not in data['total_sum']:
                    data['total_sum']['ticket_num'] = ticket_num
                else:
                    data['total_sum']['ticket_num'] += ticket_num
                if 'ticket_price' not in data['total_sum']:
                    data['total_sum']['ticket_price'] = ticket_price
                else:
                    data['total_sum']['ticket_price'] += ticket_price
            rules = {}
            lave_price = 0.0
            if type == 'all' or type == 'salary' or type == 'leave':
                for rule in rules_ids:
                    rule_amount = termination_model.compute_rule(rule, emp.contract_id)
                    if type == 'all' or type == 'salary':
                        rules[rule.name] = rule_amount
                        name = rule.name
                        if name not in data['total_rule']:
                            data['total_rule'][name] = rule_amount
                        else:
                            data['total_rule'][name] += rule_amount
                    salary += rule_amount
                if type == 'all' or type == 'salary':
                    if 'total_salary' not in data['total_rule']:
                        data['total_rule']['total_salary'] = salary
                    else:
                        data['total_rule']['total_salary'] += salary
                    data[emp.name]['rule'] = rules
                    data[emp.name]['total_salary'] = salary
                if type == 'all' or type == 'leave':
                    if salary > 0:
                        amount_per_day = salary / 30
                        lave_price = emp.remaining_leaves * amount_per_day
                    if 'lave_price' not in data['total_sum']:
                        data['total_sum']['lave_price'] = lave_price
                    else:
                        data['total_sum']['lave_price'] += lave_price
            data[emp.name]['leave_price'] = lave_price
            if type == 'all' or type == 'termination':
                if 'five_year_price' not in data['total_sum']:
                    data['total_sum']['termination_price'] = cause_amount
                    data['total_sum']['five_year_price'] = five_cause_amount
                    data['total_sum']['amount'] = amount
                else:
                    data['total_sum']['termination_price'] += cause_amount
                    data['total_sum']['five_year_price'] += five_cause_amount
                    data['total_sum']['amount'] += amount
            key_list.append(emp.name)
            total = data[emp.name]['total_salary'] + data[emp.name]['termination_price'] + data[emp.name][
                'leave_price'] + data[emp.name]['ticket_price']
            data[emp.name]['total'] = total
            if 'total' not in data['total_sum']:
                data['total_sum']['total'] = total
            else:
                data['total_sum']['total'] += total
        mykey = list(dict.fromkeys(key_list))
        return data, mykey

    @api.model
    def _get_report_values(self, docids, data=None):
        data_dic, mykey = self.get_value(data)
        allowance_ids = data['form']['allowance_ids']
        len_of_salary = len(allowance_ids)
        type = data['form']['type']
        date_to = data['form']['date_to']
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'type': type,
            'data': data_dic,
            'mykey': mykey,
            'len_of_salary': len_of_salary,
            'date_to': date_to,
        }
class TerminationReportXls(models.AbstractModel):
    _name = 'report.hr_termination.termination_benefits_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, datas):
        x = self.env['report.hr_termination.termination_report_temp']
        final_dic, mykey = ReportTerminationPublic.get_value(x, data)
        type = data['form']['type']
        allowance_ids = data['form']['allowance_ids']
        len_of_salary = len(allowance_ids)
        sheet = workbook.add_worksheet(U'Holiday Report')
        sheet.right_to_left()
        format2 = workbook.add_format(
            {'font_size': 10, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
             'bold': True})
        format2.set_align('center')
        format2.set_align('vcenter')
        sheet.merge_range('B2:P2', _("تقرير المخصصات حتى تاريخ") + data['form']['date_to'], format2)
        sheet.write(3, 1, ('اسم الموظف'), format2)
        sheet.write(3, 2, ('تاريخ المباشرة '), format2)
        z = 'D' + str(4)
        y = 'E' + str(3)
        x = len_of_salary + 3
        not_salary = 3
        if type == 'all' or type == 'salary':
            sheet.merge_range(3, 3, 3, x, ('الراتب الشهري '), format2)
            flag = 1
            x = 3
            for key in mykey:
                if flag == 1:
                    for rule in final_dic[key]['rule']:
                        sheet.write(4, x, rule, format2)
                        x += 1
                    flag += 1
                sheet.write(4, len_of_salary + 3, ('المجموع'), format2)
            sheet.write(3, len_of_salary + 4, ('سنوات الخدمة(سنة/شهر/يوم)'), format2)
            sheet.write(3, len_of_salary + 5, ('سبب إنهاء الخدمة'), format2)
        else:
            sheet.write(3, not_salary, ('سنوات الخدمة(سنة/شهر/يوم)'), format2)
            sheet.write(3, not_salary + 1, ('سبب إنهاء الخدمة'), format2)
        if type == 'leave':
            sheet.write(3, not_salary + 2, ('رصيد الإجازة'), format2)
            sheet.write(3, not_salary + 3, ('قيمة الإجازة'), format2)
        if type == 'all':
            sheet.write(3, len_of_salary + 6, ('رصيد الإجازة'), format2)
            sheet.write(3, len_of_salary + 7, ('عدد تذاكر السفر المستحقة'), format2)
            sheet.write(3, len_of_salary + 8, ('مبلغ تذكرة السفر'), format2)
            sheet.write(3, len_of_salary + 9, ('قيمة الإجازة'), format2)
            sheet.merge_range(3, len_of_salary + 10, 3, len_of_salary + 11, ('نهاية الخدمة '), format2)
            sheet.write(4, len_of_salary + 10, ('نهاية الخدمة لأقل من 5 سنة'), format2)
            sheet.write(4, len_of_salary + 11, ('نهاية الخدمة لأكبر من 5 سنة'), format2)
            sheet.write(3, len_of_salary + 12, ('قيمة نهاية الخدمة'), format2)
            sheet.write(3, len_of_salary + 13, ('إجمالي المستحق'), format2)
        if type == 'ticket':
            sheet.write(3, not_salary + 2, ('عدد تذاكر السفر المستحقة'), format2)
            sheet.write(3, not_salary + 3, ('مبلغ تذكرة السفر'), format2)
        if type == 'termination':
            sheet.merge_range(3, not_salary + 2, 3, not_salary + 3, ('قيمة نهاية الخدمة '), format2)
            sheet.write(4, not_salary + 2, ('نهاية الخدمة لأقل من5 سنة'), format2)
            sheet.write(4, not_salary + 3, ('قيمة نهاية الخدمة لأكبر من 5 سنة'), format2)
            sheet.write(3, not_salary + 5, ('قيمة نهاية الخدمة'), format2)
            sheet.write(3, not_salary + 4, ('إجمالي المستحق'), format2)

        if type == 'salary':
            sheet.write(3, len_of_salary + 6, ('إجمالي المستحق'), format2)
        if type != 'salary' and type != 'all' and type != 'termination':
            sheet.write(3, not_salary + 4, ('إجمالي المستحق'), format2)
        row = 4
        for key in mykey:
            row += 1
            n = 3
            data_row = 3
            sheet.write(row, 1, final_dic[key]['employee_name'], format2)
            sheet.write(row, 2, final_dic[key]['date'], format2)
            if type == 'all' or type == 'salary':
                for rule in final_dic[key]['rule']:
                    sheet.write(row, n, final_dic[key]['rule'][rule], format2)
                    n += 1
                sheet.write(row, data_row + len_of_salary, final_dic[key]['total_salary'], format2)
                sheet.write(row, data_row + len_of_salary + 1, final_dic[key]['experiences_year'], format2)
                sheet.write(row, data_row + len_of_salary + 2, final_dic[key]['termination_reson'], format2)
            else:
                sheet.write(row, data_row, final_dic[key]['experiences_year'], format2)
                sheet.write(row, data_row + 1, final_dic[key]['termination_reson'], format2)
            if type == 'leave':
                sheet.write(row, data_row + 2, final_dic[key]['remind_leave_day'], format2)
                sheet.write(row, data_row + 3, final_dic[key]['leave_price'], format2)
            if type == 'all':
                sheet.write(row, data_row + len_of_salary + 3, final_dic[key]['remind_leave_day'], format2)
                sheet.write(row, data_row + len_of_salary + 4, final_dic[key]['ticket'], format2)
                sheet.write(row, data_row + len_of_salary + 5, final_dic[key]['ticket_price'], format2)
                sheet.write(row, data_row + len_of_salary + 6, final_dic[key]['leave_price'], format2)
                sheet.write(row, data_row + len_of_salary + 7, final_dic[key]['five_year_price'], format2)
                sheet.write(row, data_row + len_of_salary + 8, final_dic[key]['amount'], format2)
                sheet.write(row, data_row + len_of_salary + 9, final_dic[key]['termination_price'], format2)
                sheet.write(row, data_row + len_of_salary + 10, final_dic[key]['total'], format2)
            if type == 'ticket':
                sheet.write(row, data_row + 2, final_dic[key]['ticket'], format2)
                sheet.write(row, data_row + 3, final_dic[key]['ticket_price'], format2)
            if type == 'termination':
                sheet.write(row, data_row + 2, final_dic[key]['five_year_price'], format2)
                sheet.write(row, data_row + 3, final_dic[key]['amount'], format2)
                sheet.write(row, data_row + 4, final_dic[key]['termination_price'], format2)
                sheet.write(row, data_row + 5, final_dic[key]['total'], format2)
            if type == 'salary':
                sheet.write(row, len_of_salary + 6, final_dic[key]['total'], format2)
            if type != 'salary' and type != 'all' and type != 'termination':
                sheet.write(row, data_row + 4, final_dic[key]['total'], format2)
        y = len(final_dic) + 1 + len_of_salary + 1
        sheet.merge_range(y, 1, y, 2, _('الاجمالى'), format2)
        m = 3
        for tot_rule in final_dic['total_rule']:
            sheet.write(y, m, final_dic['total_rule'][tot_rule], format2)
            m += 1
        m = m + 2
        if type == 'all' or type == 'leave':
            sheet.write(y, m, final_dic['total_sum']['remaining_leaves'], format2)
        if type == 'all' or type == 'ticket':
            sheet.write(y, m + 1, final_dic['total_sum']['ticket_num'], format2)
            sheet.write(y, m + 2, final_dic['total_sum']['ticket_price'], format2)
        if type == 'all' or type == 'leave':
            sheet.write(y, m + 3, final_dic['total_sum']['lave_price'], format2)
        if type == 'all' or type == 'termination':
            sheet.write(y, m + 4, final_dic['total_sum']['five_year_price'], format2)
            sheet.write(y, m + 5, final_dic['total_sum']['amount'], format2)
            sheet.write(y, m + 6, final_dic['total_sum']['termination_price'], format2)
        sheet.write(y, m + 7, final_dic['total_sum']['total'], format2)