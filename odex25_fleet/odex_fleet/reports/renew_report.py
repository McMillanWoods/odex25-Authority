# -*- coding: utf-8 -*-

import io
import base64
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

from datetime import datetime,timedelta,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import arabic_reshaper
from bidi.algorithm import get_display
import io
import base64

# Form Renew
# renew
class Renew(models.AbstractModel):
    _name = 'report.odex_fleet.renew_report_pdf'
    _description = 'Report Renew'

    def get_result(self, data=None):
        form = data
        domain = [('state','=', 'approve')]
        if form['date_from'] and form['date_to']:
            domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
        form = self.env['form.renew'].sudo().search(domain)
        return form


    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.get_result(data)
        date_to, date_from = ' / ', ' / '
        if data['date_from'] and data['date_to']:
            date_from = data['date_from']
            date_to = data['date_to']
        return {
            'date_from': date_from,
            'date_to': date_to,
            'docs': record,
        }
# To renew
class ToRenew(models.AbstractModel):
    _name = 'report.odex_fleet.to_renew_report_pdf'
    _description = 'Report To Renew'

    def get_result(self, data=None):
        form = data
        domain = []
        if form['date_from'] and form['date_to']:
            domain = [('form_end', '>=', form['date_from']), ('form_end', '<=', form['date_to'])]
        form = self.env['fleet.vehicle'].sudo().search(domain)
        return form


    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.get_result(data)
        date_to, date_from = ' / ', ' / '
        if data['date_from'] and data['date_to']:
            date_from = data['date_from']
            date_to = data['date_to']
        return {
            'date_from': date_from,
            'date_to': date_to,
            'docs': record,
        }