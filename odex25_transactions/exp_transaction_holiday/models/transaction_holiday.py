# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class TransactionHoliday(models.Model):
    _name = 'transaction.holiday'
    _rec_name = 'year'

    year = fields.Integer(
        "Calendar Year",
        required=True,
        default=date.today().year
    )
    name = fields.Char(string="Name")
    weekend_ids = fields.One2many('transaction.weekend.holiday', 'holiday_id', string='Weekend Days',
                                  ondelete='cascade')
    public_holiday_ids = fields.One2many('transaction.public.holiday', 'holiday_id', string='Public Holiday',
                                         ondelete='cascade')


class TransactionWeekendHoliday(models.Model):
    _name = 'transaction.weekend.holiday'

    name = fields.Selection(selection=[('saturday', 'Saturday'),
                                       ('sunday', 'Sunday'),
                                       ('monday', 'Monday'),
                                       ('tuesday', 'Tuesday'),
                                       ('wednesday', 'Wednesday'),
                                       ('thursday', 'Thursday'),
                                       ('friday', 'Friday')], string='Day Off', required=True)
    holiday_id = fields.Many2one('transaction.holiday', string='Holiday', store=True)

    @api.constrains('holiday_id')
    def check_name(self):
        rec = self.env['transaction.weekend.holiday'].search(
            [('holiday_id', '=', self.holiday_id.id), ('id', '!=', self.id),
             ('name', '=', self.name)])
        if rec:
            raise Warning(_('Day off name must be unique in year'))


class TransactionPublicHoliday(models.Model):
    _name = 'transaction.public.holiday'

    name = fields.Char(string="Name", required=True)
    holiday_id = fields.Many2one('transaction.holiday', string='Holiday', store=True)
    from_date = fields.Date(string="From Date", default=fields.date.today(), required=True)
    to_date = fields.Date(string="To Date", default=fields.date.today(), required=True)

    @api.constrains('from_date', 'to_date')
    def check_dates(self):
        if self.from_date > self.to_date:
            raise Warning(_('Date from must be less than date to'))

    @api.constrains('holiday_id')
    def check_date(self):
        rec = self.env['transaction.public.holiday'].search(
            [('holiday_id', '=', self.holiday_id.id), ('id', '!=', self.id),
             ('from_date', '<=', self.to_date),
             ('to_date', '>=', self.from_date)])
        if rec:
            raise Warning(_('You cannot create a new holiday in the same year in the same period'))
