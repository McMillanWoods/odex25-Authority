from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HRCustom(models.Model):
    _inherit = 'hr.employee'

    driver = fields.Boolean(string="Is Driver")
    license_type = fields.Selection(selection=[('private', 'Private'), ('general', 'General'), ('public', 'Public')],
                                    string="License Type")
    license_number = fields.Char(string="License Number")
    license_start = fields.Date(string="License Start")
    license_end = fields.Date(string="License End")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    old_vehicle_id = fields.Many2one('fleet.vehicle', string="Old Vehicle")
    delegation_start = fields.Date(string="Delegation Start Date")
    delegation_end = fields.Date(string="Delegation End Date")
    receive_date = fields.Date(string="Receive  Date",readonly=True)
    license_attache = fields.Binary(string="License Attachment")
    employee_cars_count = fields.Integer(compute="_compute_employee_cars_count", string="Cars",groups="base.group_user")

    def _compute_employee_cars_count(self):
        driver_ids = (self.mapped('user_id.partner_id') | self.sudo().mapped('address_home_id')).ids
        fleet_data = self.env['fleet.vehicle.assignation.log'].read_group(
            domain=[('driver_id', 'in', driver_ids)], fields=['vehicle_id:array_agg'], groupby=['driver_id'])
        mapped_data = {
            group['driver_id'][0]: len(set(group['vehicle_id']))
            for group in fleet_data
        }
        for employee in self:
            drivers = employee.user_id.partner_id | employee.sudo().address_home_id
            employee.employee_cars_count = sum(mapped_data.get(pid, 0) for pid in drivers.ids)

    @api.onchange('delegation_start', 'receive_date')
    def _onchange_delegation_start(self):
        for r in self:
            r.receive_date = r.delegation_start

    @api.model
    def driver_expired_cron(self):
        date = datetime.now().date()
        license = self.company_id.license
        if license > 0:
            date = date + relativedelta(days=license)
            fleet = self.env['hr.employee'].sudo().search([('driver','=',True),('license_end', '<=', str(date))])
            for f in fleet:
                template = self.env.ref('odex_fleet.driver_expiration_email_template', False)
                template.send_mail(f.id)


