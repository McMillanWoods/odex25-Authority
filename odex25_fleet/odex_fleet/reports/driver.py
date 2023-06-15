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

  # driver

class Driver(models.AbstractModel):
    _name = 'report.odex_fleet.driver_report_pdf'
    _description = 'Report Driver'

    def get_result(self, data=None):
        form = data
        domain = [('driver','=',True),('vehicle_id','!=',False)]
        if form['state_ids']:
            domain += [('branch_id.state_id','in',form['state_ids'])]
        if form['date_from'] and form['date_to']:
            domain = [('delegation_start', '>=', form['date_from']), ('delegation_end', '<=', form['date_to'])]
        if form['department_ids']:
            domain += [('department_id.name','in',form['department_ids'])]
        emp = self.env['hr.employee'].sudo().search(domain)
        return emp

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

  # driver Delegation

class DriverDelegation(models.AbstractModel):
    _name = 'report.odex_fleet.driver_delegation_report_pdf'
    _description = 'Report Delegation'

    def get_result(self, data=None):
        form = data
        domain = [('delegation_type','=','driver'),('state','=','in_progress')]
        if form['state_ids']:
            domain += [('vehicle_id.branch_id.state_id','in',form['state_ids'])]
        # if form['date_from'] and form['date_to']:
        #     domain += [('start_date', '>=', form['date_from']), ('end_date', '<=', form['date_to'])]
        emp = self.env['vehicle.delegation'].sudo().search(domain)
        return emp

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