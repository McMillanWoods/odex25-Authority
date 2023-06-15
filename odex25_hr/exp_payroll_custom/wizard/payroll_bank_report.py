# -*- coding:utf-8 -*-

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class BankPayslipReport(models.TransientModel):
    _name = 'payroll.bank.wiz'
    _description = "Bank Payslips Report"

    date_from = fields.Date(string='Date From', required=True,
                            default=lambda self: date(date.today().year, date.today().month, 1))
    date_to = fields.Date(string='Date To', required=True,
                          default=lambda self: date(date.today().year, date.today().month, 1) + relativedelta(months=1,
                                                                                                              days=-1))

    bank_ids = fields.Many2many('res.bank', string='Banks', required=True)
    salary_ids = fields.Many2many('hr.payroll.structure', 'payroll_bank_salary_rel', string='Salary Structures')
    level_ids = fields.Many2many('hr.payroll.structure', 'payroll_bank_level_rel', string='Salary Levels')
    group_ids = fields.Many2many('hr.payroll.structure', 'payroll_bank_group_rel', string='Salary Groups')
    degree_ids = fields.Many2many('hr.payroll.structure', 'payroll_bank_degree_rel', string='Salary Degrees')
    employee_ids = fields.Many2many('hr.employee', string='Employees')

    @api.onchange('date_from')
    def onchange_date_from(self):
        if self.date_from:
            self.date_to = fields.Date.from_string(self.date_from) + relativedelta(months=+1, day=1, days=-1)

    def print_pdf_report(self):
        self.ensure_one()
        [data] = self.read()
        date_from = self.date_from
        date_to = self.date_to
        employees = self.env['hr.employee'].search([('id', 'in', self.employee_ids.ids)])
        banks = self.env['res.bank'].search([('id', 'in', self.bank_ids.ids)])
        salary = self.env['hr.payroll.structure'].search([('id', 'in', self.salary_ids.ids)])

        datas = {
            'employees': employees.ids,
            'banks': banks.ids,
            'salary': salary.ids,
            'form': data,
            'date_from': date_from,
            'date_to': date_to,
        }

        return self.env.ref('exp_payroll_custom.bank_payslip_report').report_action(self, data=datas)

    def print_report(self):
        [data] = self.read()
        date_from = self.date_from
        date_to = self.date_to
        employees = self.env['hr.employee'].search([('id', 'in', self.employee_ids.ids)])
        banks = self.env['res.bank'].search([('id', 'in', self.bank_ids.ids)])
        salary = self.env['hr.payroll.structure'].search([('id', 'in', self.salary_ids.ids)])

        datas = {
            'employees': employees.ids,
            'banks': banks.ids,
            'salary': salary.ids,
            'form': data,
            'date_from': date_from,
            'date_to': date_to,
        }

        return self.env.ref('exp_payroll_custom.report_payroll_bank_xlsx').report_action(self, data=datas)
