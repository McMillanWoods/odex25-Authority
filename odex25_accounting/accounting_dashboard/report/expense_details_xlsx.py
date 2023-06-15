# -*- coding: utf-8 -*-

from odoo import models, _
from datetime import datetime, timedelta
from collections import OrderedDict


class ExpenseDetailsXlsx(models.AbstractModel):
    _name = 'report.report_expense_details_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        # self._define_formats(workbook)

        months, lines, total = self.expense_lines(date_from, date_to)
        self.report_generation(workbook, date_from, date_to, months, lines, total)

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
    def expense_lines(self, from_date, to_date):
        dates = [from_date, to_date]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        months_between = OrderedDict(((start + timedelta(_)).strftime(r"%B-%Y"),
                                      None) for _ in range((end - start).days)).keys()
        months_between = list(months_between)
        expense_type_id = self.env.ref('account.data_account_type_expenses').id

        select_clause = """SELECT date_trunc('month', l.date) AS amount_month,
                    a.code AS code, a.id AS id, a.name AS name,\
                    COALESCE(SUM(l.debit), 0) - COALESCE(SUM(l.credit), 0) as amount 
                    """

        from_clause = """
                    FROM account_account a\
                    LEFT JOIN account_move_line l ON (a.id=l.account_id)\
                    LEFT JOIN account_move m ON (l.move_id=m.id)\
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                    LEFT JOIN account_journal j ON (l.journal_id=j.id) 
                    """

        where_clause = """
                    WHERE a.user_type_id = (%s)
                    AND  l.date BETWEEN to_date(%s, 'yyyy-mm-dd') AND to_date(%s, 'yyyy-mm-dd')
                    AND m.state = 'posted'
                    """

        group_by_clause = """
                    GROUP BY a.id, a.name, amount_month ORDER BY name, amount_month
                    """
        sql = (select_clause + from_clause + where_clause + group_by_clause)

        self.env.cr.execute(sql, (expense_type_id, from_date, to_date,))

        account_lines = self.env.cr.dictfetchall()

        table_data = []
        lang = self.env['res.users'].browse(self._uid).lang
        account_names = self.env['account.account'].search([('user_type_id','=',expense_type_id)])
        expenses_by_month = {}
        for month_year in months_between:
            expenses_by_month[month_year] = 0

        for account in account_names:
            acc_total = 0
            account_list = [account.code, account.with_context({'lang': lang}).name]
            account_data_by_month = []
            account_account_lines = [al for al in account_lines if al['id'] == account.id]
            for month_year in months_between:
                expenses_by_month[month_year] += sum([al['amount']
                                                      for al in account_account_lines
                                                      if al['amount_month'].strftime(r"%B-%Y") == month_year])
                if month_year in [al['amount_month'].strftime(r"%B-%Y") for al in account_account_lines]:
                    month_amount = [al['amount'] for al in account_account_lines
                                    if al['amount_month'].strftime(r"%B-%Y") == month_year][0]
                    account_list.append(month_amount)
                    account_data_by_month.append(month_amount)
                    acc_total += month_amount
                else:
                    account_list.append(0)
                    account_data_by_month.append(0)
            account_list.append(acc_total)
            table_data.append(account_list)
        return months_between, table_data, list(expenses_by_month.values())

    def report_generation(self, workbook, date_from, date_to, months, lines, total):
        item_sheet = workbook.add_worksheet(_("Expenses"))
        item_format1,lines_format4 = self._define_formats(workbook)
        lang = self.env['res.users'].browse(self._uid).lang
        if self.env['res.lang'].search([('code', '=', lang)]).direction == 'rtl':
            item_sheet.right_to_left()


        item_sheet.hide_gridlines(2)
        item_sheet.set_default_row(25)

        item_sheet.set_column(0, 0, 15)
        item_sheet.set_column(1, 1, 25)
        item_sheet.set_column(2,len(months)+2, 15)
        row = 0
        header = _('Expenses for Period (%s - %s)')%(date_from,date_to)
        item_sheet.merge_range(row, 0, row,len(months)+2, header , item_format1)

        row += 2
        item_sheet.merge_range(row, 0, row+1, 0, _('Code'), item_format1)
        item_sheet.merge_range(row, 1, row+1, 1, _('Name'),item_format1)
        item_sheet.merge_range(row, 2, row, len(months)+2, _('Expenses'), item_format1)

        row += 1
        for col, month in enumerate(months):
            item_sheet.write(row, col+2, month, item_format1)
        item_sheet.write(row, col+3, _('Total'), item_format1)

        for record in lines:
            row += 1
            for i, r in enumerate(record):
                item_sheet.write(row, i, r, lines_format4)

        row += 1
        item_sheet.merge_range(row, 0, row, 1, _('Total'), item_format1)
        for i, t in enumerate(total):
            item_sheet.write(row, i+2, t, item_format1)
        item_sheet.write(row, i + 3, sum(total), item_format1)

        row += 2
        item_sheet.write(row, 0, _('Prepare'))
        item_sheet.write(row, 3, _('Review'))
        item_sheet.write(row, 7, _('Approve'))

        row += 1
        item_sheet.write(row, 0, _('Date'))
        item_sheet.write(row, 3, _('Date'))
        item_sheet.write(row, 7, _('Date'))

        row += 1
        item_sheet.write(row, 0, _('Signature'))
        item_sheet.write(row, 3, _('Signature'))
        item_sheet.write(row, 7, _('Signature'))
