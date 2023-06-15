# -*- coding: utf-8 -*-

import io
import base64
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

from datetime import datetime,timedelta,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class FleetMaintainsReport(models.AbstractModel):
    _name = 'report.odex_fleet.maintains_report_pdf'
    _description = 'Report Mainatains'

    def get_result(self, data=None):
        form = data
        domain = []
        if form['branch_ids']:
            domain += [('branch_id','in',form['branch_ids'])]
        if form['report_type']:
            domain += [('state','in',['draft','confirm'])] if form['report_type'] == 'to_maintains' else  [('state','in',['approve','paid'])]
        if form['date_from'] and form['date_to']:
            domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
        if form['department_ids']:
            domain += [('vehicle_id.department_id.name', 'in', form['department_ids'])]
        request = self.env['fleet.maintenance'].sudo().search(domain,order="id desc")
        return request


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
            'report_type': data['report_type'],
            'docs': record,
        }

