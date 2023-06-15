from odoo import models, fields, api, _
from datetime import datetime, date


class ExpenseReportWiz(models.TransientModel):
    _name = 'expense.report.wiz'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    def print_report(self):
        res = {'date_from': self.date_from, 'date_to': self.date_to}
        return self.env.ref('accounting_dashboard.report_expense_details_xlsx').report_action(self, data=res)

