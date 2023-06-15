# -*- coding: utf-8 -*-

import io
import base64
import matplotlib.pyplot as plt
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

from datetime import datetime,timedelta,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import arabic_reshaper
from bidi.algorithm import get_display
import io
import base64

class FleetBranchReport(models.AbstractModel):
    _name = 'report.odex_fleet.fleet_branch_report_pdf'
    _description = 'Report Branch'
    def get_result(self, data=None):
        form = data
        domain = [('invoice_id','!=', False)]
        if form['branch_ids']:
            domain += [('branch_id','in',form['branch_ids'])]
        if form['type_ids']:
            domain += [('vehicle_id.fleet_type_id','in',form['type_ids'])]
        if form['date_from'] and form['date_to']:
            domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
        if form['vehicle_del_type'] == 'department':
            domain += [('vehicle_id.department_id.name', 'in', form['department_ids'])]
        if form['vehicle_del_type'] == 'project' :
            domain += [('vehicle_id.project_id.name', 'in', form['project_ids'])]
        service = self.env['fleet.vehicle.log.services'].sudo().search(domain)
        fuel = self.env['fleet.vehicle.log.fuel'].sudo().search(domain)
        branch = self.env['res.branch'].browse(form['branch_ids']) if form['branch_ids'] else set(service.mapped('branch_id') + fuel.mapped('branch_id'))
        types = self.env['fleet.type'].browse(form['type_ids']) if form['type_ids'] else set(service.mapped('vehicle_id.fleet_type_id') + fuel.mapped('vehicle_id.fleet_type_id'))
        data = {}
        li = []
        for b in branch:
            b_service = service.filtered(lambda r:r.branch_id == b)
            b_fuel = fuel.filtered(lambda r:r.branch_id == b)
            rec = []
            for t in types:
                value = {}
                value['type'] = t.name
                value['total'] = sum(b_service.filtered(lambda r:r.vehicle_id.fleet_type_id == t).mapped('amount')) +\
                             sum(b_fuel.filtered(lambda r:r.vehicle_id.fleet_type_id == t).mapped('amount')) or 0
                rec.append(value)
            li.append({'branch':b.name,'data':rec,'total':sum(b_service.mapped('amount'))+sum(b_fuel.mapped('amount')) or 0})
        tot = []
        for t in types:
            amount = sum(service.filtered(lambda r:r.vehicle_id.fleet_type_id == t and r.branch_id in branch).mapped('amount')) +\
                             sum(fuel.filtered(lambda r:r.vehicle_id.fleet_type_id == t and r.branch_id in branch).mapped('amount')) or 0
            tot.append([t.name,amount])
        data['total'] = tot
        data['branch'] = sorted(li, key=lambda d: d['total'], reverse=False)
        return data
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
    
#     cost chart

class FleetChartReport(models.AbstractModel):
    _name = 'report.odex_fleet.all_branch_cost_report_pdf'
    _description = 'Report Branch Cost'

    def get_chart(self, cdata,type=False):
        print("ffffffffffffffff",cdata)
        li = []
        labels, slices = [], []
        for dic in cdata:
            if type:
                labels.append(get_display(arabic_reshaper.reshape(dic['type'])))
            else:
                labels.append(get_display(arabic_reshaper.reshape(dic['branch'])))
            slices.append(round(dic['total_per'],2))
        textprops = {"fontsize": 9}
        plt.pie(slices, labels=labels, autopct='%1.1f%%', shadow=True, startangle=15, textprops=textprops, )
        plt.axis('equal')
        buffered = io.BytesIO()
        plt.savefig(buffered, format='png')
        plt.close()
        return base64.b64encode(buffered.getvalue())

    def bar_get_chart(self, datas,type=False):
        li = []
        for cdata in datas:
            labels, slices = [], []
            for dic in cdata['data']:
                labels.append(get_display(arabic_reshaper.reshape(dic['branch'])))
                slices.append(round(dic['total_per'],2))
            line = plt.bar(labels, slices)
            plt.xlabel('Percentage')
            plt.ylabel("Branch")
            for i in range(len(slices)):
                plt.annotate(str(slices[i]), xy=(labels[i], slices[i]), ha='center', va='bottom')
            # plt.show()
            buffered = io.BytesIO()
            plt.savefig(buffered, format='png')
            plt.close()
            li.append(base64.b64encode(buffered.getvalue()))
        return li

    def get_result(self, data=None):
        form = data
        domain = []
        if form['branch_ids']:
            domain += [('branch_id','in',form['branch_ids'])]
        if form['date_from'] and form['date_to']:
            domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
        if form['type_ids']:
            domain += [('vehicle_id.fleet_type_id','in',form['type_ids'])]
        if form ['vehicle_del_type'] == 'department':
            domain += [('vehicle_id.department_id.name','in',form['department_ids'])]
        if form ['vehicle_del_type'] == 'project':
            domain += [('vehicle_id.project_id.name','in',form['project_ids'])]

        man = self.env['fleet.maintenance'].sudo().search(domain)
        domain += [('invoice_id','!=', False)]
        service = self.env['fleet.vehicle.log.services'].sudo().search(domain)
        fuel = self.env['fleet.vehicle.log.fuel'].sudo().search(domain)
        branch = self.env['res.branch'].browse(form['branch_ids']) if form['branch_ids'] else set(service.mapped('branch_id') + fuel.mapped('branch_id')+man.mapped('branch_id')+ man.mapped('branch_id')+man.mapped('branch_id'))
        types = self.env['fleet.type'].browse(form['type_ids']) if form['type_ids'] else set(service.mapped('vehicle_id.fleet_type_id') + fuel.mapped('vehicle_id.fleet_type_id')+man.mapped('vehicle_id.fleet_type_id'))
        totals_alls = sum(service.mapped('amount')) + sum(fuel.mapped('amount')) + sum(man.mapped('total_cost'))

        data = {}
        li = []
        tot = []
        l = []
        for t in types:
            value = {}
            value['type'] = t.name
            total = sum(service.filtered(lambda r: r.vehicle_id.fleet_type_id == t).mapped('amount')) + \
                    sum(fuel.filtered(lambda r: r.vehicle_id.fleet_type_id == t).mapped('amount')) + \
                    sum(man.filtered(lambda r: r.vehicle_id.fleet_type_id == t).mapped('total_cost'))
            total_per = total / totals_alls * 100 if totals_alls > 0 else 0
            value['total'] = total
            value['total_per'] = total_per
            l.append(value)
            rec = []
            for b in branch:
                datas = {}
                branch_total = sum(
                    service.filtered(lambda r: r.vehicle_id.fleet_type_id == t and r.branch_id == b).mapped('amount')) + \
                               sum(fuel.filtered(lambda r: r.vehicle_id.fleet_type_id == t and r.branch_id == b).mapped(
                                   'amount')) +sum(man.filtered(lambda r: r.vehicle_id.fleet_type_id == t and r.branch_id == b).mapped(
                                   'total_cost'))
                branch_total_per = branch_total / totals_alls * 100 if totals_alls > 0 else 0
                datas['branch'] = b.name
                datas['total'] = branch_total
                datas['total_per'] = branch_total_per
                rec.append(datas)
                branch_branch = sum(
                    service.filtered(lambda r:r.branch_id == b).mapped('amount')) + \
                               sum(fuel.filtered(lambda r:r.branch_id == b).mapped('amount')) + sum(
                    man.filtered(lambda r:r.branch_id == b).mapped( 'total_cost'))
                branch_per = branch_branch / totals_alls * 100 if totals_alls > 0 else 0
                tot.append({'branch': b.name, 'total': branch_branch, 'total_per': branch_per})
            li.append({'type': t.name, 'data': sorted(rec, key=lambda d: d['total'], reverse=True)})
        tot = [dict(t) for t in {tuple(d.items()) for d in tot}]
        data['branch'] = sorted(tot, key=lambda d: d['total'], reverse=True)
        data['types'] = sorted(l, key=lambda d: d['total'], reverse=True)
        data['branch_types'] = li
        data['chart'] = self.get_chart(tot)
        data['chart_main'] = self.get_chart(l,type=True)
        data['bar_chart'] = self.bar_get_chart(li,type=True)


        return data


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



# state

class AllStateReport(models.AbstractModel):
    _name = 'report.odex_fleet.state_cost_report_pdf'
    _description = 'Report State Cotst'

    def get_result(self, data=None):
        form = data
        domain = [('invoice_id','!=', False)]
        if form['state_ids']:
            domain += [('branch_id.state_id','in',form['state_ids'])]
        if form['type_ids']:
            domain += [('vehicle_id.fleet_type_id','in',form['type_ids'])]
        if form['date_from'] and form['date_to']:
            domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
        service = self.env['fleet.vehicle.log.services'].sudo().search(domain)
        fuel = self.env['fleet.vehicle.log.fuel'].sudo().search(domain)
        branch = list(set(service.mapped('branch_id') + fuel.mapped('branch_id')))
        state = self.env['res.country.state'].browse(form['state_ids']) if form['state_ids'] else list(set(service.mapped('branch_id.state_id') + fuel.mapped('branch_id.state_id')))
        types = self.env['fleet.type'].browse(form['type_ids']) if form['type_ids'] else set(service.mapped('vehicle_id.fleet_type_id') + fuel.mapped('vehicle_id.fleet_type_id'))
        last = []
        for s in state:
            data = {}
            li = []
            for b in branch:
                if b.state_id == s:
                    b_service = service.filtered(lambda r:r.branch_id == b)
                    b_fuel = fuel.filtered(lambda r:r.branch_id == b)
                    rec = []
                    for t in types:
                        value = {}
                        value['type'] = t.name
                        value['total'] = sum(b_service.filtered(lambda r:r.vehicle_id.fleet_type_id == t).mapped('amount')) +\
                                     sum(b_fuel.filtered(lambda r:r.vehicle_id.fleet_type_id == t).mapped('amount')) or 0
                        rec.append(value)
                    li.append({'branch':b.name,'data':sorted(rec, key=lambda d: d['total'], reverse=False),'total':sum(b_service.mapped('amount'))+sum(b_fuel.mapped('amount')) or 0})
            tot = []
            total_state = 0
            for t in types:
                amount = sum(service.filtered(lambda r:r.vehicle_id.fleet_type_id == t and r.branch_id.state_id == s).mapped('amount')) +\
                                 sum(fuel.filtered(lambda r:r.vehicle_id.fleet_type_id == t  and r.branch_id.state_id == s).mapped('amount')) or 0
                total_state += amount
                tot.append([t.name,amount])
            data['total'] = tot
            data['branch'] = li
            data['state'] = s.name
            data['state_total'] = total_state
            last.append(data)
        return last


    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.get_result(data)
        print("ffffffffffffffffffff",record)
        date_to, date_from = ' / ', ' / '
        if data['date_from'] and data['date_to']:
            date_from = data['date_from']
            date_to = data['date_to']
        return {
            'date_from': date_from,
            'date_to': date_to,
            'docs': record,
        }


# consumption

# class FleetConsumptionReport(models.AbstractModel):
#     _name = 'report.odex_fleet.car_consumption_cost_report_pdf'
#
#     def get_result(self, data=None):
#         form = data
#         domain = []
#         if form['branch_ids']:
#             domain += [('branch_id','in',form['branch_ids'])]
#         if form['date_from'] and form['date_to']:
#             domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
#         man = self.env['fleet.maintenance'].sudo().search(domain)
#         domain += [('invoice_id','!=', False)]
#         service = self.env['fleet.vehicle.log.services'].sudo().search(domain)
#         fuel = self.env['fleet.vehicle.log.fuel'].sudo().search(domain)
#         branch = self.env['res.branch'].browse(form['branch_ids']) if form['branch_ids'] else set(service.mapped('branch_id') + fuel.mapped('branch_id')+man.mapped('branch_id')+ man.mapped('branch_id')+man.mapped('branch_id'))
#         types = self.env['fleet.type'].browse(form['type_ids']) if form['type_ids'] else set(service.mapped('vehicle_id.fleet_type_id') + fuel.mapped('vehicle_id.fleet_type_id')+man.mapped('vehicle_id.fleet_type_id'))
#         print("gggggggggggggggggg",types,branch)
#         data = {}
#         li = []
#         for b in branch:
#             b_service = service.filtered(lambda r:r.branch_id == b)
#             b_fuel = fuel.filtered(lambda r:r.branch_id == b)
#             b_man = man.filtered(lambda r: r.branch_id == b)
#             service_total = sum (b_service.mapped('amount'))
#             fuel_total = sum (b_fuel.mapped('amount'))
#             man_total = sum (b_man.mapped('total_cost'))
#             totals = service_total+fuel_total+man_total
#             service_total_per =service_total/totals*100 if totals>0 else 0
#             fuel_total_per =fuel_total/totals*100 if totals>0 else 0
#             man_total_per =man_total/totals*100 if totals>0 else 0
#             total_per = man_total_per+fuel_total_per+service_total_per
#             data['total'] = [[service_total,fuel_total,man_total,totals],[service_total_per,fuel_total_per,man_total_per,total_per]]
#             vehicle_ids = list(set(service.mapped('vehicle_id') + fuel.mapped('vehicle_id') + man.mapped('vehicle_id')))
#             rec = []
#             for t in types:
#                 l =[]
#                 value = {}
#                 value['type'] = t.name
#                 print("dddddddddddd",vehicle_ids)
#                 # fuel_total_b = 0
#                 # man_total_b = 0
#                 # service_total_b = 0
#                 fuel_total_b = sum(b_fuel.filtered(lambda r: r.vehicle_id.fleet_type_id == t).mapped('amount'))
#                 man_total_b = sum(b_man.filtered(lambda r: r.vehicle_id.fleet_type_id == t).mapped('total_cost'))
#                 service_total_b = sum(b_service.filtered(lambda r: r.vehicle_id.fleet_type_id == t).mapped('amount'))
#                 total_total = service_total+man_total+fuel_total
#                 total_total_per = totals/ total_total *100if total_total>0 else 0
#                 for c in vehicle_ids:
#                     if c.fleet_type_id == t:
#                         z = {}
#                         z['name'] = c.name
#                         z['model'] = c.model_id.name
#                         z['driver'] = c.employee_id.name
#                         z['plate'] = c.license_plate
#                         z['job'] = c.employee_id.job_id.name
#                         z['fuel'] = sum(b_fuel.filtered(lambda r:r.vehicle_id == c and r.vehicle_id.fleet_type_id == t).mapped('amount'))
#                         z['man'] = sum(b_man.filtered(lambda r:r.vehicle_id == c  and r.vehicle_id.fleet_type_id == t).mapped('total_cost'))
#                         z['service'] = sum(b_service.filtered(lambda r:r.vehicle_id == c  and r.vehicle_id.fleet_type_id == t).mapped('amount'))
#                         z['total'] = z['fuel'] + z['man'] + z['service']
#                         z['all_tot_per'] = z['total']/total_total*100 if total_total>0 else 0
#                         # print("fffffffffff444", z['all_tot_per'] , total_total,z['total'],total_total_per)
#                         # total_total_per += z['all_tot_per']
#                         # fuel_total_b +=  z['fuel']
#                         # man_total_b +=  z['man']
#                         # service_total_b +=  z['service']
#                         l.append(z)
#                 value['data'] = l
#                 value['type'] = t.name
#                 value['total'] = [fuel_total_b,service_total_b,man_total_b,total_total,total_total_per]
#                 rec.append(value)
#             li.append({'branch':b.name,'data':rec,'total':[fuel_total_b,service_total_b,man_total_b,total_total,total_total_per]})
#         data['branch'] = li
#         return data
#
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         record = self.get_result(data)
#         print("ddddddddddddddd",record)
#         date_to, date_from = ' / ', ' / '
#         if data['date_from'] and data['date_to']:
#             date_from = data['date_from']
#             date_to = data['date_to']
#         return {
#             'date_from': date_from,
#             'date_to': date_to,
#             'docs': record,
#         }
# # Form Renew
# # renew
# class Renew(models.AbstractModel):
#     _name = 'report.odex_fleet.renew_report_pdf'
#
#     def get_result(self, data=None):
#         form = data
#         domain = [('state','=', 'approve')]
#         if form['date_from'] and form['date_to']:
#             domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
#         form = self.env['form.renew'].sudo().search(domain)
#         return form
#
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         record = self.get_result(data)
#         date_to, date_from = ' / ', ' / '
#         if data['date_from'] and data['date_to']:
#             date_from = data['date_from']
#             date_to = data['date_to']
#         return {
#             'date_from': date_from,
#             'date_to': date_to,
#             'docs': record,
#         }
# # To renew
# class ToRenew(models.AbstractModel):
#     _name = 'report.odex_fleet.to_renew_report_pdf'
#
#     def get_result(self, data=None):
#         form = data
#         domain = []
#         if form['date_from'] and form['date_to']:
#             domain = [('form_end', '>=', form['date_from']), ('form_end', '<=', form['date_to'])]
#         form = self.env['fleet.vehicle'].sudo().search(domain)
#         return form
#
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         record = self.get_result(data)
#         date_to, date_from = ' / ', ' / '
#         if data['date_from'] and data['date_to']:
#             date_from = data['date_from']
#             date_to = data['date_to']
#         return {
#             'date_from': date_from,
#             'date_to': date_to,
#             'docs': record,
#         }
#   # driver

# class Driver(models.AbstractModel):
#     _name = 'report.odex_fleet.driver_report_pdf'
#
#     def get_result(self, data=None):
#         form = data
#         domain = [('driver','=',True),('vehicle_id','!=',False)]
#         if form['state_ids']:
#             domain += [('branch_id.state_id','in',form['state_ids'])]
#         if form['date_from'] and form['date_to']:
#             domain = [('delegation_start', '>=', form['date_from']), ('delegation_end', '<=', form['date_to'])]
#         emp = self.env['hr.employee'].sudo().search(domain)
#         return emp
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         record = self.get_result(data)
#         date_to, date_from = ' / ', ' / '
#         if data['date_from'] and data['date_to']:
#             date_from = data['date_from']
#             date_to = data['date_to']
#         return {
#             'date_from': date_from,
#             'date_to': date_to,
#             'docs': record,
#         }
#
#   # driver Delegation
#
# class DriverDelegation(models.AbstractModel):
#     _name = 'report.odex_fleet.driver_delegation_report_pdf'
#
#     def get_result(self, data=None):
#         form = data
#         domain = [('delegation_type','=','driver'),('state','=','approve')]
#         if form['state_ids']:
#             domain += [('vehicle_id.branch_id.state_id','in',form['state_ids'])]
#         if form['date_from'] and form['date_to']:
#             domain += [('start_date', '>=', form['date_from']), ('end_date', '<=', form['date_to'])]
#         emp = self.env['vehicle.delegation'].sudo().search(domain)
#         return emp
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         record = self.get_result(data)
#         date_to, date_from = ' / ', ' / '
#         if data['date_from'] and data['date_to']:
#             date_from = data['date_from']
#             date_to = data['date_to']
#         return {
#             'date_from': date_from,
#             'date_to': date_to,
#             'docs': record,
#         }
# Service
# class AllStateServiceReport(models.AbstractModel):
#     _name = 'report.odex_fleet.service_report_pdf'
#
#     def get_result(self, data=None):
#         form = data
#         domain = [('invoice_id','!=', False)]
#         if form['state_ids']:
#             domain += [('branch_id.state_id','in',form['state_ids'])]
#         if form['type_ids']:
#             domain += [('fleet_type_id','in',form['type_ids'])]
#         if form['date_from'] and form['date_to']:
#             domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
#         service = self.env['fleet.vehicle.log.services'].sudo().search(domain)
#         branch = service.mapped('branch_id')
#         state = self.env['res.country.state'].browse(form['state_ids']) if form['state_ids'] else service.mapped('branch_id.state_id')
#         last = []
#         for s in state:
#             data = {}
#             li = []
#             for b in branch:
#                 if b.state_id == s:
#                     b_service = service.filtered(lambda r:r.branch_id == b)
#                     rec = []
#                     for z in b_service:
#                         for t in z.cost_ids:
#                             value = {}
#                             value['name'] = z.vehicle_id.employee_id.name
#                             value['cost'] = t.amount
#                             value['service'] = t.cost_subtype_id.name
#                             value['vehicle'] = z.vehicle_id.fleet_type_id.name
#                             value['license_number'] = z.vehicle_id.license_plate
#                             rec.append(value)
#                 li.append({'branch':b.name,'data':rec,'total':sum(b_service.mapped('amount')) or 0})
#             data['branch'] = li
#             data['state'] = s.name
#             last.append(data)
#         print("RRRRRRRRRRRRRRRRRR",last)
#         return last
#
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         record = self.get_result(data)
#         date_to, date_from = ' / ', ' / '
#         if data['date_from'] and data['date_to']:
#             date_from = data['date_from']
#             date_to = data['date_to']
#         return {
#             'date_from': date_from,
#             'date_to': date_to,
#             'docs': record,
#         }
#  # Invoice
# class Invoice(models.AbstractModel):
#     _name = 'report.odex_fleet.invoice_report_pdf'
#
#     def get_result(self, data=None):
#         form = data
#         domain = [('invoice_id','!=', False)]
#         if form['vehicle_ids']:
#             domain += [('vehicle_id','in',form['vehicle_ids'])]
#         date = 0
#         if form['date_from'] and form['date_to']:
#             date = fields.Datetime.from_string(form['date_to']) - fields.Datetime.from_string(form['date_from'])
#             date = date.days
#             domain += [('date', '>=', form['date_from']), ('date', '<=', form['date_to'])]
#         service = self.env['fleet.vehicle.log.fuel'].sudo().search(domain)
#         # service_types = self.env['fleet.service.type'].browse(form['service_ids']) if form['service_ids'] else service.mapped('vehicle_id.fleet_type_id')
#         vehicle_ids = self.env['fleet.vehicle'].browse(form['vehicle_ids'])
#         li = []
#         print("IIIIIIIIIIIIII",date)
#         for v in vehicle_ids:
#             b_service = service.filtered(lambda r:r.vehicle_id == v)
#             invoice = b_service.mapped('invoice_id')
#             if invoice:
#                 rec = {}
#                 rec['service'] = "Fuel"
#                 rec['car'] = v.name
#                 rec['driver'] = v.employee_id.name
#                 rec['type'] = v.fleet_type_id.name
#                 l = []
#                 total = 0
#                 for t in invoice:
#                     value = {}
#                     value['date'] = t.date_invoice
#                     value['number'] = t.number
#                     value['amount'] = t.amount_total
#                     total += t.amount_total
#                     l.append(value)
#                 rec['data'] = l
#                 rec['total'] = total
#                 rec['date'] = date
#                 liter = round(sum(b_service.mapped('liter'))/date,2)
#                 rec['liter'] = liter
#                 rec['liter_price'] = round(total/liter,2)
#                 li.append(rec)
#         return li
#
#
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         record = self.get_result(data)
#         print("OOOOOOOOOOOOOOOOOO",record)
#         date_to, date_from = ' / ', ' / '
#         if data['date_from'] and data['date_to']:
#             date_from = data['date_from']
#             date_to = data['date_to']
#         return {
#             'date_from': date_from,
#             'date_to': date_to,
#             'docs': record,
#         }