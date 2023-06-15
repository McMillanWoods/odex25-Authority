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

# consumption
class FleetConsumptionReport(models.AbstractModel):
    _name = 'report.odex_fleet.car_consumption_cost_report_pdf'
    _description = 'Report Consumption'

    def get_result(self, data=None):
        form = data
        domain = []
        if form['vehicle_ids']:
            domain += [('vehicle_id','in',form['vehicle_ids'])]
        if form['type_ids']:
            domain += [('vehicle_id.fleet_type_id','in',form['type_ids'])]
        if form['branch_ids']:
            domain += [('branch_id','in',form['branch_ids'])]
        if form['date_from'] and form['date_to']:
            domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
        if form['department_ids']:
            domain += [('vehicle_id.department_id.name', 'in', form['department_ids'])]
        man = self.env['fleet.maintenance'].sudo().search(domain)
        domain += [('invoice_id','!=', False)]
        service = self.env['fleet.vehicle.log.services'].sudo().search(domain)
        fuel = self.env['fleet.vehicle.log.fuel'].sudo().search(domain)
        branch = self.env['res.branch'].browse(form['branch_ids']) if form['branch_ids'] else set(service.mapped('branch_id') + fuel.mapped('branch_id')+man.mapped('branch_id')+ man.mapped('branch_id')+man.mapped('branch_id'))
        types = self.env['fleet.type'].browse(form['type_ids']) if form['type_ids'] else set(service.mapped('vehicle_id.fleet_type_id') + fuel.mapped('vehicle_id.fleet_type_id')+man.mapped('vehicle_id.fleet_type_id'))
        data = {}
        li = []
        for b in branch:
            b_service = service.filtered(lambda r:r.branch_id == b)
            b_fuel = fuel.filtered(lambda r:r.branch_id == b)
            b_man = man.filtered(lambda r: r.branch_id == b)
            service_total = sum (b_service.mapped('amount'))
            fuel_total = sum (b_fuel.mapped('amount'))
            man_total = sum (b_man.mapped('total_cost'))
            totals = service_total+fuel_total+man_total
            service_total_per =service_total/totals*100 if totals>0 else 0
            fuel_total_per =fuel_total/totals*100 if totals>0 else 0
            man_total_per =man_total/totals*100 if totals>0 else 0
            total_per = man_total_per+fuel_total_per+service_total_per
            total_values = [[service_total,fuel_total,man_total,totals],[service_total_per,fuel_total_per,man_total_per,total_per]]
            vehicle_ids = list(set(b_service.mapped('vehicle_id') + b_fuel.mapped('vehicle_id') + b_man.mapped('vehicle_id')))
            rec = []
            for t in types:
                l =[]
                value = {}
                fuel_total_b = sum(b_fuel.filtered(lambda r: r.vehicle_id.fleet_type_id == t).mapped('amount'))
                man_total_b = sum(b_man.filtered(lambda r: r.vehicle_id.fleet_type_id == t).mapped('total_cost'))
                service_total_b = sum(b_service.filtered(lambda r: r.vehicle_id.fleet_type_id == t).mapped('amount'))
                total_total = fuel_total_b+man_total_b+service_total_b
                total_total_per = 0
                for c in vehicle_ids:
                    if c.fleet_type_id == t:
                        z = {}
                        z['name'] = c.name
                        z['model'] = c.model_id.name
                        z['driver'] = c.employee_id.name
                        z['plate'] = c.license_plate
                        z['job'] = c.employee_id.job_id.name
                        z['fuel'] = sum(b_fuel.filtered(lambda r:r.vehicle_id == c and  r.vehicle_id.fleet_type_id == t).mapped('amount'))
                        z['man'] = sum(b_man.filtered(lambda r:r.vehicle_id == c and  r.vehicle_id.fleet_type_id == t).mapped('total_cost'))
                        z['service'] = sum(b_service.filtered(lambda r:r.vehicle_id == c and  r.vehicle_id.fleet_type_id == t).mapped('amount'))
                        z['total'] = z['fuel'] + z['man'] + z['service']
                        z['all_tot_per'] = z['total']/total_total*100 if total_total>0 else 0
                        total_total_per += z['all_tot_per']
                        l.append(z)
                value['data'] = sorted(l, key=lambda d: d['total'], reverse=True)
                value['type'] = t.name
                value['total'] = [fuel_total_b,service_total_b,man_total_b,total_total,total_total_per]
                rec.append(value)
            li.append({'branch':b.name,'data':rec,'total':total_values})
        return li


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
# Service
class AllStateServiceReport(models.AbstractModel):
    _name = 'report.odex_fleet.service_report_pdf'
    _description = 'Report Fleet Service'

    def get_result(self, data=None):
        form = data
        domain = [('invoice_id','!=', False)]
        if form['state_ids']:
            domain += [('branch_id.state_id','in',form['state_ids'])]
        if form['type_ids']:
            domain += [('vehicle_id.fleet_type_id','in',form['type_ids'])]
        if form['date_from'] and form['date_to']:
            domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
        if form['state_ids']:
            domain += [('branch_id.state_id','in',form['state_ids'])]
        if form['cost_subtype_ids']:
            print("==================",form['cost_subtype_ids'])
            domain += [('cost_subtype_id','in',form['cost_subtype_ids'])]
        if form['department_ids']:
            domain += [('vehicle_id.department_id.name', 'in', form['department_ids'])]

        service = self.env['fleet.vehicle.log.services'].sudo().search(domain)
        print("=================",service)
        branch = service.mapped('branch_id')
        state = self.env['res.country.state'].browse(form['state_ids']) if form['state_ids'] else service.mapped('branch_id.state_id')
        last = []
        for s in state:
            data = {}
            li = []
            for b in branch:
                if b.state_id == s:
                    b_service = service.filtered(lambda r:r.branch_id == b)
                    rec = []
                    for z in b_service:

                        for t in z.cost_ids:
                            value = {}
                            value['name'] = z.vehicle_id.employee_id.name
                            value['cost'] = t.total
                            value['service'] = t.cost_subtype_id.name
                            value['vehicle'] = z.vehicle_id.fleet_type_id.name
                            value['license_number'] = z.vehicle_id.license_plate
                            value['date'] = z.date
                            rec.append(value)
                    li.append({'branch':b.name,'data':rec,'total':sum(b_service.mapped('amount')) or 0})
            data['branch'] = li
            data['state'] = s.name
            last.append(data)
        return last


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
 # Invoice
class Invoice(models.AbstractModel):
    _name = 'report.odex_fleet.invoice_report_pdf'
    _description = 'Report Invoice'

    def get_result(self, data=None):
        form = data
        domain = [('invoice_id','!=', False)]
        if form['vehicle_ids']:
            domain += [('vehicle_id','in',form['vehicle_ids'])]
        date = 0
        if form['date_from'] and form['date_to']:
            date = fields.Datetime.from_string(form['date_to']) - fields.Datetime.from_string(form['date_from'])
            date = date.days
            domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
        if form['vehicle_del_type'] == 'department':
            domain += [('vehicle_id.department_id.name', 'in', form['department_ids'])]
        if form['vehicle_del_type'] == 'project' :
            domain += [('vehicle_id.project_id.name', 'in', form['project_ids'])]
        service = self.env['fleet.vehicle.log.fuel'].sudo().search(domain)
        # service_types = self.env['fleet.service.type'].browse(form['service_ids']) if form['service_ids'] else service.mapped('vehicle_id.fleet_type_id')
        vehicle_ids = self.env['fleet.vehicle'].browse(form['vehicle_ids']) if form['vehicle_ids'] else service.mapped('vehicle_id')
        li = []
        for v in vehicle_ids:
            b_service = service.filtered(lambda r:r.vehicle_id == v)
            invoice = b_service.mapped('invoice_id')
            if invoice:
                rec = {}
                rec['service'] = "Fuel"
                rec['car'] = v.name
                rec['driver'] = v.employee_id.name
                rec['type'] = v.fleet_type_id.name
                price = v.fuel_type.price
                print("fffffffff",price)
                l = []
                total = 0
                for t in invoice:
                    value = {}
                    value['date'] = t.invoice_date

                    # value['number'] = t.ref

                    value['amount'] = t.amount_total
                    total += t.amount_total
                    l.append(value)
                rec['data'] = l
                rec['total'] = total
                rec['date'] = date
                liter = round(total/date if date>0 else 0,2)
                rec['liter'] = liter
                rec['liter_price'] = round(liter/price if price>0 else 0,2)
                # rec['liter_price'] = round(total/liter if liter>0 else 0,2)
                li.append(rec)
        return li



    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.get_result(data)
        print("OOOOOOOOOOOOOOOOOO",record)
        date_to, date_from = ' / ', ' / '
        if data['date_from'] and data['date_to']:
            date_from = data['date_from']
            date_to = data['date_to']
        return {
            'date_from': date_from,
            'date_to': date_to,
            'docs': record,
        }
