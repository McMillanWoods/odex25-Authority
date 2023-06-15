from odoo import models, fields, api, _


class DriverDepartment(models.Model):
    _name = 'driver.department'
    # _rec_name = 'driver_department_id'

    name = fields.Char('Name' , related = "department_id.name")
    department_id = fields.Many2one('hr.department', string='Department')
    branch_id = fields.Many2one('res.branch', string='Branch')