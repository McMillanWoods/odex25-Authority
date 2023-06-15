# -*- coding: utf-8 -*-

from odoo import fields, models,_
from datetime import date,datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import pendulum



class WeekGenerationWizard(models.TransientModel):
    _name = 'week.generation.wizard'
    _description = 'Week Generation Wizard'

    def get_years(self):
        res = []
        year = datetime.today() + relativedelta(years=1)
        year = year.year
        YEARS = [year - i for i in range(6)]
        for y in YEARS:
            res.append((str(y),str(y)))
        return res

    year = fields.Selection(selection=lambda self: self.get_years(),string="Years")

    def get_week_name(self,start_date):
        """ Generates a week name
        """
        res = {}
        year_week = start_date.strftime('%Y-%U')
        res['name'] = year_week
        pendulum.week_starts_at(pendulum.SUNDAY)
        pendulum.week_ends_at(pendulum.SATURDAY)
        pendulum_date = pendulum.datetime(start_date.year, start_date.month, start_date.day)
        start = pendulum_date.start_of('week')
        end = pendulum_date.end_of('week')
        res['date_from'] =  start
        res['date_to'] = end
        return res

    def generate_week(self):
        values = []
        start_date = datetime.now().date().replace(year=int(self.year),month=1, day=1)
        end_date = datetime.now().date().replace(year=int(self.year),month=12, day=31)
        weeks_in_start_year = int(date(start_date.year, 12, 28).strftime("%U"))
        start_week = start_date.strftime("%U")
        end_week = end_date.strftime("%U")
        if start_week ==  end_week:
            start_date = start_date + relativedelta(days=7)
            start_week = start_date.strftime("%U")
        for week in range(0, (int(end_week) - int(start_week)) + 1):
            res = self.get_week_name(start_date + relativedelta(days=7 * week))
            values.append(res)
        self.env['week.week'].create(values)
        return True


    # def generate_week(self):
    #     values = []
    #     start_date = datetime.now().date().replace(year=int(self.year),month=1, day=1)
    #     end_date = datetime.now().date().replace(year=int(self.year),month=12, day=31)
    #     weeks_in_start_year = int(date(start_date.year, 12, 28).isocalendar()[1])
    #     start_week = start_date.isocalendar()[1]
    #     end_week = end_date.isocalendar()[1]
    #     if start_week ==  end_week:
    #         start_date = start_date + relativedelta(days=7)
    #         start_week = start_date.isocalendar()[1]
    #     for week in range(0, (end_week - start_week) % weeks_in_start_year + 1):
    #         res = self.get_week_name(start_date + relativedelta(days=7 * week))
    #         values.append(res)
    #     self.env['week.week'].create(values)
    #     return True
