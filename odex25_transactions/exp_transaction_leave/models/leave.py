# -*- coding: utf-8 -*-

from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class Leave(models.Model):
    _name = 'employee.leave'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    _description = 'for mange transaction in employee leave'

    # name = fields.Char(string='Transaction Number')
    state = fields.Selection(selection=[('draft', 'Draft'), ('request', 'Request'), ('refuse', 'Refuse'),
                                        ('approve', 'Approved'), ('expired', 'Expired')], string='State',
                             default='draft')
    from_date = fields.Date(string='From Date', default=fields.Date.today)
    to_date = fields.Date(string='To Date')
    employee_id = fields.Many2one(comodel_name='cm.entity', string='Employee',
                                  default=lambda self: self.default_employee_id(), readonly=True)
    alternative_employee_ids = fields.One2many('employee.leave.line', 'leave_id', string='Alternative Employees')
    alternative_manager_ids = fields.One2many('manager.leave.line', 'leave_id', string='Alternative Mangers')
    current_is_manager = fields.Boolean(string='Is Manager', compute="set_is_manager")

    def default_employee_id(self):
        user = self.env.user
        em = self.env['cm.entity'].search([('user_id', '=', user.id)], limit=1)
        return len(em) and em or self.env['cm.entity']

    @api.constrains('employee_id')
    def constrains_leave(self):
        rec = self.env['employee.leave'].search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                                 ('from_date', '<=', self.to_date),
                                                 ('to_date', '>=', self.from_date),
                                                 ('state', 'in', ['request', 'approve'])])
        if rec:
            raise Warning(_('You can not create new leave for employee have leave in sam duration'))

    def set_is_manager(self):
        user_id = self.env['res.users'].browse(self.env.uid)
        if self.employee_id.parent_id.manager_id.user_id == user_id:
            self.current_is_manager = True
        else:
            self.current_is_manager = False

    ####################################################
    # Business methods
    ####################################################
    def action_request(self):
        for rec in self:
            rec.state = 'request'

    def action_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    def action_approve(self):
        for rec in self:
            rec.state = 'approve'

    def action_expired(self):
        date_now = date.today()
        leave_ids = self.env['employee.leave'].search([('to_date', '<', date_now), ('state', '=', 'approve')])
        if leave_ids:
            for leave in leave_ids:
                leave.state = 'expired'


class LeaveLine(models.Model):
    _name = 'employee.leave.line'
    _rec_name = 'employee_id'
    _description = 'for mange transaction in employee leave line'

    unit_id = fields.Many2one(comodel_name='cm.entity', string='Unit', domain=lambda self: self.onchange_leave_id())
    employee_id = fields.Many2one(comodel_name='cm.entity', string='Employee',
                                  domain=lambda self: self.onchange_unit_id())
    leave_id = fields.Many2one(comodel_name='employee.leave', string="Leave")

    @api.onchange('leave_id')
    def onchange_leave_id(self):
        domain = {}
        if self.leave_id:
            domain = {'unit_id': [('id', 'in', self.env['cm.entity'].search([('type', '=', 'unit'),
                                                                             ('secretary_id', '=',
                                                                              self.leave_id.employee_id.id)]).ids)]}
        return {'domain': domain}

    @api.onchange('unit_id')
    def onchange_unit_id(self):
        domain = {}
        if self.leave_id:
            domain = {'employee_id': [('id', 'in', self.env['cm.entity'].search([('type', '=', 'employee'),
                                                                                 ('parent_id', '=',
                                                                                  self.unit_id.id),
                                                                                 ('id', '!=',
                                                                                  self.leave_id.employee_id.id)]).ids)]}
        return {'domain': domain}


class MangerLeaveLine(models.Model):
    _name = 'manager.leave.line'
    _rec_name = 'employee_id'
    _description = 'for mange transaction in employee leave line'

    unit_id = fields.Many2one(comodel_name='cm.entity', string='Unit', domain=lambda self: self.onchange_leave_id())
    employee_id = fields.Many2one(comodel_name='cm.entity', string='Employee',
                                  domain=lambda self: self.onchange_unit_id())
    leave_id = fields.Many2one(comodel_name='employee.leave', string="Leave")

    @api.onchange('leave_id')
    def onchange_leave_id(self):
        domain = {}
        if self.leave_id:
            domain = {'unit_id': [('id', 'in', self.env['cm.entity'].search([('type', '=', 'unit'),
                                                                             ('manager_id', '!=', False),
                                                                             ('manager_id', '=',
                                                                              self.leave_id.employee_id.id)]).ids)]}
        return {'domain': domain}

    @api.onchange('unit_id')
    def onchange_unit_id(self):
        domain = {}
        if self.leave_id:
            domain = {'employee_id': [('id', 'in', self.env['cm.entity'].search([('type', '=', 'employee'),
                                                                                 ('parent_id', '=',
                                                                                  self.unit_id.id),
                                                                                 ('id', '!=',
                                                                                  self.leave_id.employee_id.id)]).ids)]}
        return {'domain': domain}


class Transaction(models.Model):
    _inherit = 'transaction.transaction'

    def get_employee_id(self, transaction):
        if transaction.to_ids:
            employee_id = transaction.to_ids[0].id
            unit_id = transaction.to_ids[0].parent_id.id
            if transaction.to_ids[0].type == 'unit':
                employee_id = transaction.to_ids[0].secretary_id.id
                unit_id = transaction.to_ids[0].id
            return employee_id, unit_id
        else:
            return False, False

    def get_employee_leave(self, employee_id, unit_id, transaction_date, ):
        employee_records = False
        record = self.env['employee.leave'].search([('employee_id', '=', employee_id),
                                                    ('from_date', '<=', transaction_date),
                                                    ('to_date', '>=', transaction_date),
                                                    ('state', '=', 'approve')])
        if record:
            employee_records = self.env['employee.leave.line'].search([('leave_id', '=', record.id),
                                                                       ('unit_id', '=',
                                                                        unit_id)]).employee_id.id
        return employee_records

    
    def compute_receive_id(self):
        for rec in self:
            employee_id, unit_id = self.get_employee_id(rec)
            rec.receive_id = employee_id
            employee_records = self.get_employee_leave(employee_id, unit_id, rec.transaction_date)
            if employee_records:
                rec.receive_id = employee_records
                rec.to_user_have_leave = True

    
    def compute_receive_manger_id(self):
        for rec in self:
            rec.receive_manger_id = False
            if rec.preparation_id:
                manager_id = self.get_employee_leave(rec.preparation_id.manager_id.id, rec.preparation_id.id,
                                                     rec.transaction_date)
                if manager_id:
                    rec.receive_manger_id = manager_id
                else:
                    rec.receive_manger_id = rec.preparation_id.manager_id
                    # rec.to_manager_have_leave = True

    def compute_have_leave(self):
        for rec in self:
            employee_id, unit_id = self.get_employee_id(rec)
            employee_records = self.get_employee_leave(employee_id, unit_id, rec.transaction_date)
            if employee_records:
                rec.to_user_have_leave = True
            else:
                rec.to_user_have_leave = False
