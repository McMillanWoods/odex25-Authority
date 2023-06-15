# -*- coding: utf-8 -*-
##############################################################################
#
#   Expert (LCT, Life Connection Technology)
#    Copyright (C) 2020-2021 LCT
#
##############################################################################
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class FleettWiz(models.TransientModel):
    _name = 'fleet.wiz'
    _description = "Fleet Wizard Report"

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    service_ids = fields.Many2many('fleet.service.type','fleet_service_wiz_rel', 'service_id', 'wiz_id', string='Service', )
    branch_ids = fields.Many2many('res.branch', string='Branch', )
    type_ids = fields.Many2many('fleet.type', string='Fleet Type', )
    vehicle_ids = fields.Many2many('fleet.vehicle', string='Vehicle', )
    state_ids = fields.Many2many('res.country.state', string=' States')
    cost_subtype_ids = fields.Many2many('fleet.service.type', string='Service Type')
    vehicle_del_type = fields.Selection(selection=[('department', 'Department'),
                                              ('project', 'Project')])
    department_ids = fields.Many2many('hr.department',string='Departments')
    project_ids = fields.Many2many('project.project',string='projects')
    report_type = fields.Selection(selection=[('branch_cost','Branch Cost'),
                                              ('state_cost','State Cost'),
                                             ('all_branch_cost', 'All Branch Cost'),
                                              ('car_consumption','Car Consumption'),
                                              ('driver','Driver'),
                                              ('delegation','Delegation'),
                                              ('renew','Renew'),
                                              ('to_renew','To Renew'),
                                              ('service','Service'),
                                              ('invoice','Invoice'),
                                              ('maintains','Maintenance'),
                                              ('to_maintains','To Maintenance'),
                                              ])



    @api.constrains('date_from','date_to')
    def check_date(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_from>rec.date_to:
                    raise ValidationError(_("Date To Should Be Greater Than Date From"))

    def print_report(self):
        data ={'state_ids':self.state_ids.ids if self.state_ids else False,'date_from':self.date_from,'date_to':self.date_to,'report_type':self.report_type,
               'type_ids':self.type_ids.ids if self.type_ids else False,'branch_ids':self.branch_ids.ids if self.branch_ids else False ,
               'vehicle_ids':self.vehicle_ids.ids if self.vehicle_ids else False,'cost_subtype_ids': self.cost_subtype_ids.ids if self.cost_subtype_ids else False,
               'vehicle_del_type' : self.vehicle_del_type if self.vehicle_del_type else False ,
               'department_ids':self.department_ids.mapped('name'),
               'project_ids':self.project_ids.mapped('name')}
        if self.report_type == 'branch_cost':
            return self.env.ref('odex_fleet.fleet_branch_report_pdf_act').report_action(self, data=data)
        elif self.report_type == 'state_cost':
            return self.env.ref('odex_fleet.state_cost_report_pdf_act').report_action(self, data=data)
        elif self.report_type == 'all_branch_cost':
            return self.env.ref('odex_fleet.all_branch_cost_report_pdf_act').report_action(self, data=data)
        elif self.report_type == 'car_consumption':
            return self.env.ref('odex_fleet.car_consumption_cost_report_pdf_act').report_action(self, data=data)
        elif self.report_type == 'to_renew':
            return self.env.ref('odex_fleet.to_renew_report_pdf_act').report_action(self, data=data)
        elif self.report_type == 'renew':
            return self.env.ref('odex_fleet.renew_report_pdf_act').report_action(self, data=data)
        elif self.report_type == 'driver':
            return self.env.ref('odex_fleet.driver_report_pdf_act').report_action(self, data=data)
        elif self.report_type == 'delegation':
            return self.env.ref('odex_fleet.driver_delegation_report_pdf_act').report_action(self, data=data)
        elif self.report_type == 'service':
            return self.env.ref('odex_fleet.service_report_pdf_act').report_action(self, data=data)
        elif self.report_type == 'service':
            return self.env.ref('odex_fleet.service_report_pdf_act').report_action(self, data=data)
        elif self.report_type == 'invoice':
            return self.env.ref('odex_fleet.invoice_report_pdf_act').report_action(self, data=data)
        elif self.report_type in ['to_maintains','maintains']:
            return self.env.ref('odex_fleet.maintains_report_pdf_act').report_action(self, data=data)
