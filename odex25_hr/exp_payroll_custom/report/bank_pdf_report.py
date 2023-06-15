# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError


class PayslipBankReport(models.AbstractModel):
    _name = 'report.exp_payroll_custom.report_payroll_bank_pdf'
    _description = 'Payroll Bank PDF report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        emp_ids = data['employees']
        bank_ids = data['banks']
        salary_ids = data['salary']
        date_from = data['date_from']
        date_to = data['date_to']
        employees = self.env['hr.employee'].browse(emp_ids)
        salary = self.env['hr.payroll.structure'].browse(salary_ids)
        banks = self.env['res.bank'].browse(bank_ids)

        data = []
        for bank in banks:
            docs = []
            if employees:
                payslips = self.env['hr.payslip'].search(
                    ['&', ('date_from', '>=', date_from), ('date_to', '<=', date_to),
                     ('employee_id', 'in', employees.ids), ('bank_id', '=', bank.id)])

            elif salary:
                payslips = self.env['hr.payslip'].search(
                    ['&', ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('struct_id', 'in', salary_ids),
                     ('bank_id', '=', bank.id)])
            elif salary and employees:
                payslips = self.env['hr.payslip'].search(
                    ['&', ('date_from', '>=', date_from), ('date_to', '<=', date_to),
                     ('employee_id', 'in', employees.ids), ('struct_id', 'in', salary.ids),
                     ('bank_id', '=', bank.id)])
            else:
                payslips = self.env['hr.payslip'].search(
                    ['&', ('date_from', '>=', date_from), ('date_to', '<=', date_to),
                     ('bank_id', '=', bank.id)])

            for payslip in payslips:
                tot_basic = 0.0
                tot_housing = 0.0
                tot_other = 0.0
                tot_net = 0.0
                tot_ded = 0.0

                net = 0.0
                basic = 0.0
                housing = 0.0
                other = 0.0
                total = 0.0
                salary_rules = self.env['hr.salary.rule'].search([]).sorted(
                    key=lambda v: v.sequence).ids
                payslip_line_obj = self.env['hr.payslip.line']
                payslip_lines_ids = payslip_line_obj.search([('slip_id', '=', payslip.id)])
                if not payslip_lines_ids:
                    continue

                for payslip_line_rec in payslip_lines_ids:
                    if payslip_line_rec.salary_rule_id.id in salary_rules:
                        if payslip_line_rec.salary_rule_id.rules_type == 'salary':
                            basic += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.rules_type == 'house':
                            housing += payslip_line_rec.total
                    other = payslip.total_allowances - basic - housing
                    deduction = total - net
                    tot_net += net
                    tot_basic += basic
                    tot_housing += housing
                    tot_other += other
                    tot_ded += deduction
                docs.append({
                    'ID': payslip.employee_id.emp_no,
                    'Name': payslip.employee_id.name,
                    'Account #': payslip.employee_id.bank_account_id.acc_number,
                    'Bank': payslip.employee_id.bank_account_id.bank_id.name,
                    'Salary': payslip.total_sum,
                    'National': payslip.employee_id.saudi_number.saudi_id if
                    payslip.employee_id.check_nationality else
                    payslip.employee_id.iqama_number.iqama_id,
                    'Basic': basic,
                    'Housing': housing,
                    'Other': other,
                    'Deduction': payslip.total_deductions,
                })
            data.append({
                'docs': docs,
                'bank': bank.name

            })

        return {
            'banks': banks,
            'data': data,
            'date_from': date_from,
            'date_to': date_to,
        }


class PayrollXlsx(models.AbstractModel):
    _name = 'report.exp_payroll_custom.report_payroll_bank_xlsx'
    _description = 'report.exp_payroll_custom.report_payroll_bank_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, payslips):
        emp_ids = data['employees']
        bank_ids = data['banks']
        salary_ids = data['salary']
        date_from = data['date_from']
        date_to = data['date_to']
        employees = self.env['hr.employee'].browse(emp_ids)
        # salary = self.env['hr.payroll.structure'].browse(salary_ids)
        banks = self.env['res.bank'].browse(bank_ids)
        salary_ids = self.env['hr.payroll.structure'].browse(salary_ids)
        print('salary ids', salary_ids, salary_ids.ids)

        sheet = workbook.add_worksheet('Hr Payslip Info')
        format1 = workbook.add_format(
            {'font_size': 10, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
             'bold': True})
        format2 = workbook.add_format(
            {'font_size': 10, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
             'bold': True})
        format3 = workbook.add_format({'bottom': True, 'align': 'center', 'bold': True, })
        format2.set_align('center')
        format2.set_align('vcenter')
        format2.set_color('white')
        format2.set_bg_color('blue')

        sheet.set_column(2, 11, 20)
        row = 2
        data_list = []
        for bank in banks:

            row += 3
            sheet.write(row - 1, 1, bank.name, format3)
            sheet.write(row, 2, 'Employee Number', format2)
            sheet.write(row, 3, 'Employee Name', format2)
            sheet.write(row, 4, 'Account #', format2)
            sheet.write(row, 5, 'Bank', format2)
            sheet.write(row, 6, 'Amount', format2)
            sheet.write(row, 7, 'Legal #', format2)
            sheet.write(row, 8, 'Employee Basic Salary', format2)
            sheet.write(row, 9, 'Housing Allowance', format2)
            sheet.write(row, 10, 'Other Earnings', format2)
            sheet.write(row, 11, 'Deductions', format2)
            row += 1
            sheet.write(row, 2, 'الرقم الوظيفي', format2)
            sheet.write(row, 3, 'إسم الموظف ', format2)
            sheet.write(row, 4, 'رقم الحساب', format2)
            sheet.write(row, 5, 'البنك', format2)
            sheet.write(row, 6, 'المبلغ', format2)
            sheet.write(row, 7, 'رقم الهويه/الإقامة', format2)
            sheet.write(row, 8, 'الراتب الاساسى', format2)
            sheet.write(row, 9, 'بدل السكن', format2)
            sheet.write(row, 10, 'دخل اخر', format2)
            sheet.write(row, 11, 'الخصومات', format2)

            if employees:
                payslip_ids = self.env['hr.payslip'].search(
                    ['&', ('date_from', '>=', date_from), ('date_to', '<=', date_to),
                     ('employee_id', 'in', employees.ids), ('bank_id', '=', bank.id)])
            elif salary_ids:
                payslip_ids = self.env['hr.payslip'].search(
                    ['&', ('date_from', '>=', date_from), ('date_to', '<=', date_to), ('struct_id', 'in', salary_ids.ids),
                     ('bank_id', '=', bank.id)])
            elif salary_ids and employees:
                payslip_ids = self.env['hr.payslip'].search(
                    ['&', ('date_from', '>=', date_from), ('date_to', '<=', date_to),
                     ('employee_id', 'in', employees.ids), ('struct_id', 'in', salary_ids.ids),
                     ('bank_id', '=', bank.id)])
            else:
                payslip_ids = self.env['hr.payslip'].search(
                    ['&', ('date_from', '>=', date_from), ('date_to', '<=', date_to),
                     ('bank_id', '=', bank.id)])

            salary_rules = self.env['hr.salary.rule'].search([]).sorted(
                key=lambda v: v.sequence).ids
            payslip_line_obj = self.env['hr.payslip.line']
            for payslip in payslip_ids:
                basic = 0.0
                housing = 0.0
                payslip_lines_ids = payslip_line_obj.search([('slip_id', '=', payslip.id)])
                if not payslip_lines_ids:
                    continue
                for payslip_line_rec in payslip_lines_ids:
                    if payslip_line_rec.salary_rule_id.id in salary_rules:
                        if payslip_line_rec.salary_rule_id.rules_type == 'salary':
                            basic += payslip_line_rec.total
                        elif payslip_line_rec.salary_rule_id.rules_type == 'house':
                            housing += payslip_line_rec.total
                other = payslip.total_allowances - basic - housing
                data_list = [payslip.employee_id.emp_no, payslip.employee_id.name or ' ',
                             payslip.employee_id.bank_account_id.acc_number or ' ',
                             payslip.employee_id.bank_account_id.bank_id.name,
                             payslip.total_sum,
                             payslip.employee_id.saudi_number.saudi_id if
                             payslip.employee_id.check_nationality else payslip.employee_id.iqama_number.iqama_id,
                             basic, housing, other, payslip.total_deductions]
                col = 1
                row += 1
                col += 1
                sheet.write(row, 2, data_list[0], format1)
                sheet.write(row, 3, data_list[1], format1)
                sheet.write(row, 4, data_list[2], format1)
                sheet.write(row, 5, data_list[3], format1)
                sheet.write(row, 6, data_list[4], format1)
                sheet.write(row, 7, data_list[5], format1)
                sheet.write(row, 8, data_list[6], format1)
                sheet.write(row, 9, data_list[7], format1)
                sheet.write(row, 10, data_list[8], format1)
                sheet.write(row, 11, data_list[9], format1)
