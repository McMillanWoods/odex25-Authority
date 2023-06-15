# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import pycompat
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    branch_id = fields.Many2one('res.branch', string='Branch')

    @api.model
    def default_get(self, flds):
        result = super(HrDepartment, self).default_get(flds)
        user_obj = self.env['res.users']
        branch_id = user_obj.browse(self.env.user.id).branch_id.id
        result['branch_id'] = branch_id
        return result

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    branch_id = fields.Many2one('res.branch', string='Branch')

    @api.model
    def default_get(self, flds):
        result = super(HrApplicant, self).default_get(flds)
        user_obj = self.env['res.users']
        branch_id = user_obj.browse(self.env.user.id).branch_id.id
        result['branch_id'] = branch_id
        return result


    @api.onchange('job_id')
    def onchange_job_id(self):
        """ Override to get branch from department """
        
        
        department = self.env['hr.department'].browse(self.department_id.id)
        self.branch_id = department.branch_id

    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else :
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({
                    'name': applicant.partner_name or contact_name,
                    'job_id': applicant.job_id.id,
                    'address_home_id': address_id,
                    'department_id': applicant.department_id.id or False,
                    'branch_id' : applicant.branch_id.id or False,
                    'address_id': applicant.company_id and applicant.company_id.partner_id
                            and applicant.company_id.partner_id.id or False,
                    'work_email': applicant.department_id and applicant.department_id.company_id
                            and applicant.department_id.company_id.email or False,
                    'work_phone': applicant.department_id and applicant.department_id.company_id
                            and applicant.department_id.company_id.phone or False})
                applicant.write({'emp_id': employee.id})
                
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        dict_act_window['context'] = {'form_view_initial_mode': 'edit'}
        dict_act_window['res_id'] = employee.id
        return dict_act_window

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    branch_id = fields.Many2one('res.branch', string='Branch')

    @api.model
    def default_get(self, flds):
        result = super(HrEmployee, self).default_get(flds)
        user_obj = self.env['res.users']
        branch_id = user_obj.browse(self.env.user.id).branch_id.id
        result['branch_id'] = branch_id
        return result
    
class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    branch_id = fields.Many2one('res.branch', string='Branch') 
    
    @api.model 
    def default_get(self, flds):
        """ Override to get default branch from employee """ 
        result = super(HrAttendance, self).default_get(flds)
        employee_id = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)

        if employee_id :
            if employee_id.branch_id :
                
                result['branch_id'] = employee_id.branch_id.id
        return result  

    
    @api.onchange('employee_id')
    def get_branch(self):
        if self.employee_id:
            if self.employee_id.branch_id:
                self.update({'branch_id':self.employee_id.branch_id})
            else:
                self.update({'branch_id': False})     
    
class HrContract(models.Model):
    _inherit = 'hr.contract'

    branch_id = fields.Many2one('res.branch', string='Branch') 
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.branch_id = self.employee_id.branch_id

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    branch_id = fields.Many2one('res.branch', string='Branch')

    @api.model
    def default_get(self, flds):
        """ Override to get default branch from employee """
        result = super(HrPayslip, self).default_get(flds)
        employee_id = self.env['hr.employee'].browse(self._context.get('active_id'))
        result['branch_id'] = employee_id.branch_id.id
        return result

    @api.onchange('employee_id')
    def get_branch(self):
        if self.employee_id:
            if self.employee_id.branch_id:
                self.update({'branch_id':self.employee_id.branch_id})
            else:
                self.update({'branch_id': False})     

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    branch_id = fields.Many2one('res.branch', string='Branch')  
    
    @api.model 
    def default_get(self, flds): 
        """ Override to get default branch from employee """
        result = super(HrExpenseSheet, self).default_get(flds)
        employee_id = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)

        if employee_id :
            if employee_id.branch_id :
                
                result['branch_id'] = employee_id.branch_id.id
        return result

    @api.onchange('employee_id')
    def get_branch(self):
        if self.employee_id:
            if self.employee_id.branch_id:
                self.update({'branch_id':self.employee_id.branch_id})
            else:
                self.update({'branch_id': False})    
           
class HrExpense(models.Model):
    _inherit = 'hr.expense'

    branch_id = fields.Many2one('res.branch', string='Branch') 
    
    @api.model 
    def default_get(self, flds): 
        """ Override to get default branch from employee """
        result = super(HrExpense, self).default_get(flds)
        
        employee_id = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)

        if employee_id :
            if employee_id.branch_id :
                result['branch_id'] = employee_id.branch_id.id
        return result 

    @api.onchange('employee_id')
    def get_branch(self):
        if self.employee_id:
            if self.employee_id.branch_id:
                self.update({'branch_id':self.employee_id.branch_id})
            else:
                self.update({'branch_id': False})       
    
                    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
