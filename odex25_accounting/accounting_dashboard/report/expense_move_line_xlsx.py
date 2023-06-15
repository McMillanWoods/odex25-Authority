# -*- coding: utf-8 -*-

from odoo import models, _
from datetime import datetime, timedelta
from collections import OrderedDict


class ExpenseMoveLineXlsx(models.AbstractModel):
    _name = 'report.report_expense_move_line_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        # self._define_formats(workbook)
        self.report_generation(workbook, date_from, date_to)

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Those formats can be used on all cell.
        """

        item_format1 = workbook.add_format({
            'border': 1,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_color': 'white',
            'bg_color': '#548235',
            'num_format': '#,##0.00_);(#,##0.00)',
        })
        lines_format4 = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'bg_color': 'white',
            'num_format': '#,##0.00_);(#,##0.00)',
        })
        return item_format1,lines_format4
    def report_generation(self, workbook, date_from, date_to):

        expense_type_id = self.env.ref('account.data_account_type_expenses').id

        item_sheet = workbook.add_worksheet(_("Expenses"))
        item_format1,lines_format4 = self._define_formats(workbook)
        lang = self.env['res.users'].browse(self._uid).lang
        if self.env['res.lang'].search([('code', '=', lang)]).direction == 'rtl':
            item_sheet.right_to_left()


        lines = self.env['account.move.line'].with_context({'lang': lang}).search([('account_id.user_type_id','=',expense_type_id),
                                                      ('date','>=',date_from), ('date','<=',date_to),
                                                      ('move_id.state','=','posted')])
        item_sheet.hide_gridlines(2)
        item_sheet.set_default_row(25)
        item_sheet.set_column(0, 0, 15)
        item_sheet.set_column(1, 2, 25)
        item_sheet.set_column(3, 3, 35)
        item_sheet.set_column(4, 5, 15)
        item_sheet.set_column(6, 6, 35)
        item_sheet.set_column(7, 9, 25)
        row = 0
        header = _('Expenses for Period (%s - %s)')%(date_from,date_to)
        item_sheet.merge_range(row, 0, row, 9, header ,item_format1)

        row += 2
        item_sheet.write(row, 0, _('Date'), item_format1)
        item_sheet.write(row, 1, _('Payment Payable to'), item_format1)
        item_sheet.write(row, 2, _('Amount'), item_format1)
        item_sheet.write(row, 3, _('Amount(in Word)'), item_format1)
        item_sheet.write(row, 4, _('Currency'), item_format1)
        item_sheet.write(row, 5, _('Invoice #'), item_format1)
        item_sheet.write(row, 6, _('Description'), item_format1)
        item_sheet.write(row, 7, _('Department Name'), item_format1)
        item_sheet.write(row, 8, _('Bank Name'), item_format1)
        item_sheet.write(row, 9, _('Expense Type'), item_format1)
        total = 0
        for l in lines:
            row += 1
            amount = l.debit or (l.credit)*-1
            total += amount
            item_sheet.write(row, 0, l.date, lines_format4)
            item_sheet.write(row, 1, l.partner_id.name, lines_format4)
            item_sheet.write(row, 2, amount, self.lines_format4)
            item_sheet.write(row, 3, l.move_id.currency_id.amount_to_text(amount),lines_format4)
            item_sheet.write(row, 4, l.move_id.currency_id.name, lines_format4)
            item_sheet.write(row, 5, l.invoice_id.number, lines_format4)
            item_sheet.write(row, 6, l.name, lines_format4)
            item_sheet.write(row, 7, l.analytic_account_id.name or '', lines_format4)
            item_sheet.write(row, 8, ', '.join(set(l.invoice_id.payment_ids.mapped('journal_id.name'))), lines_format4)
            item_sheet.write(row, 9, l.account_id.name, lines_format4)

        item_sheet.write(row+1, 2, total, lines_format4)

