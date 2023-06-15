# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import fields , models, api


class TransactionHoliday(models.Model):
    _inherit = 'transaction.transaction'

    @api.depends('transaction_date', 'important_id')
    def compute_due_date(self):
        """method for compute due date base on holiday config(add by fatima 20/4/2020)"""
        self.due_date = False
        for record in self:
            if not len(record.important_id) or not record.transaction_date:
                continue
            rank = record.important_id.rank or 1
            final_rank = rank + record.add_rank
            year = fields.Date.to_string(record.transaction_date).split('-')[0]
            holiday_id = self.env['transaction.holiday'].search([('year', '=', year)], limit=1,
                                                                order="create_date desc")
            date = datetime.strptime(fields.Date.to_string(record.transaction_date), DEFAULT_SERVER_DATE_FORMAT)
            due = date
            number_of_plus_day = 0
            last_day_in_day = date + timedelta(days=final_rank)
            last_date = last_day_in_day - due
            holiday_line_id = self.env['transaction.public.holiday'].search(
                [('holiday_id', '=', holiday_id.id),
                 ('from_date', '<=', str(last_day_in_day).split(' ')[0]),
                 ('to_date', '>=', str(due).split(' ')[0])])
            if holiday_line_id:
                counter = 0
                data_start = datetime.strptime(holiday_line_id.from_date, DEFAULT_SERVER_DATE_FORMAT)
                end_date = datetime.strptime(holiday_line_id.to_date, DEFAULT_SERVER_DATE_FORMAT)
                number_of_plus_day = (end_date - data_start).days
                all_hol_day = [str(data_start + timedelta(days=x)).split(' ')[0] for x in range(number_of_plus_day + 1)]
                for dat in all_hol_day:
                    if dat > record.transaction_date:
                        counter += 1
                number_of_plus_day = counter
            dt = [due + timedelta(days=x) for x in range(last_date.days + 1)]
            for ddt in dt:
                date_name = ddt.strftime("%A").lower()
                weekend_id = holiday_id.weekend_ids.filtered(
                    lambda r: r.name == date_name)
                if weekend_id:
                    number_of_plus_day += 1
                y = holiday_id.public_holiday_ids.filtered(
                    lambda r: r.from_date <= str(ddt).split(' ')[0] <= r.to_date)
                if weekend_id and y:
                    number_of_plus_day -= 1
            last = final_rank + number_of_plus_day
            for i in range(last):
                due = due + timedelta(days=1)
            record.due_date = due.strftime(DEFAULT_SERVER_DATE_FORMAT)
