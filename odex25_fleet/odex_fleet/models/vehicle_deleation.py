from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class VehicleDelegation(models.Model):
    _name = 'vehicle.delegation'
    _description = 'Vehicle Deleagation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    branch_id = fields.Many2one('res.branch', string="Branch",related="driver_department.branch_id")
    old_branch_id = fields.Many2one('res.branch', string="Old Branch")
    employee_id = fields.Many2one('hr.employee', string="Driver",
                                  domain="[('driver', '=', True),('vehicle_id', '=', False)]")
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm'),
                                        ('approve', 'Approved'),
                                        ('in_progress', 'In Progress'),
                                        ('refused', 'Refused'),
                                        ('cancel', 'Cancel'),
                                        ('close', 'Close'), ], default='draft')
    company_id = fields.Many2one('res.company', string='Company')
    project_id = fields.Many2one('project.project', string='Project')
    delegation_type = fields.Selection(selection=[('branch', 'Branch'), ('driver', 'driver')],
                                       string="Delegation Type")
    license_number = fields.Char(string="License Number", related='employee_id.license_number', store=True)
    license_end = fields.Date(string="License End")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", )

    license_plate = fields.Char(required=True, related='vehicle_id.license_plate', store=True,
                                )
    vin_sn = fields.Char('Chassis Number', related='vehicle_id.vin_sn', store=True,
                         copy=False)
    model_id = fields.Many2one('fleet.vehicle.model', 'Model', related='vehicle_id.model_id', store=True, )
    fleet_type_id = fields.Many2one('fleet.type', string="Fleet Type", related='vehicle_id.fleet_type_id', store=True, )
    serial_number = fields.Char(related='vehicle_id.serial_number', string="Serial Number")
    state_id = fields.Many2one('res.country.state', string="State", )
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    reason = fields.Text(string="Reject Reason",  tracking=True,)
    custody_id = fields.Many2one('custom.employee.custody')
    entity_type = fields.Selection(selection=[('department', 'Department'), ('project', 'Project')],
                                       string="Entity Type")
    driver_department = fields.Many2one('driver.department')
    first_odometer = fields.Float(string='First Odometer',compute="get_first_odometer", store=True)
    odometer = fields.Float(string='Last Odometer',related="vehicle_id.odometer", store=True,
                            help='Odometer measure of the vehicle at the moment of this log')
    km_number = fields.Integer(string='KM Number', compute='get_km', store=True)
    last_department_id = fields.Many2one(related='vehicle_id.department_id', string="Last Department")
    last_project_id = fields.Many2one('project.project', string='Last Project', compute="get_last_project", store=True)
    last_branch_id = fields.Many2one('res.branch', string="Last Branch", compute="get_last_branch", store=True)
    delegation_create_date = fields.Date('Delegation Creation Date', readonly=True, default=fields.Date.context_today)


    @api.depends("vehicle_id")
    def get_first_odometer(self):
        for rec in self :
            if rec.vehicle_id:
                odometer_id =  self.env['fleet.vehicle.odometer'].search([('vehicle_id','=',rec.vehicle_id.id),('date','<=',rec.delegation_create_date)],limit=1)
                rec.first_odometer = odometer_id.value

    # @api.depends("vehicle_id")
    # def get_odometer(self):
    #     for rec in self:
    #         if rec.vehicle_id:
    #             rec.odometer = rec.vehicle_id.odometer

    @api.depends("vehicle_id")
    def get_last_project(self):
        for rec in self:
            obj = self.search([('vehicle_id', '=', rec.vehicle_id.name)],limit=1)
            rec.last_project_id = obj.project_id

    @api.depends("vehicle_id")
    def get_last_branch(self):
        for rec in self:
            rec.last_branch_id = rec.vehicle_id.branch_id

    # @api.onchange('branch_id')
    # def onchange_branch(self):
    #     for rec in self:
    #         rec.vehicle_id.branch_id = rec.branch_id

    @api.depends('odometer', 'first_odometer')
    def get_km(self):
        for rec in self :
            rec.km_number = rec.odometer - rec.first_odometer

    def create_custody(self):
        print("ok")
#         for rec in self:
#             custody = rec.env['custom.employee.custody'].sudo().create({
#                 'from_hr_department': True,
#                 'employee_id': rec.employee_id.id,
#             })
#             line = rec.env['employee.custody.line'].sudo().create({
#                 'name': (_("Car Delegation %s")) % rec.vehicle_id.name,
#                 'quantity': 1.0,
#                 'employee_custody_line': custody.id,
#             })
#             custody.sudo().submit()
#             rec.custody_id = custody.id

    @api.constrains('vehicle_id', 'delegation_type', 'employee_id', 'start_date', 'end_date')
    def car_constrain(self):
        for rec in self:
            if self.start_date and self.end_date:
                clause_1 = ['&', ('end_date', '<=', rec.end_date), ('end_date', '>=', rec.start_date)]
                clause_2 = ['&', ('start_date', '<=', rec.end_date), ('start_date', '>=', rec.start_date)]
                clause_3 = ['&', ('start_date', '<=', rec.start_date), ('end_date', '>=', rec.end_date)]
                value = [('id', '!=', self.id), ('state', 'not in', ['close', 'cancel']), '|',
                         '|'] + clause_1 + clause_2 + clause_3
                record = self.env['vehicle.delegation'].sudo().search(value)
                v = record.filtered(lambda r: r.id != self.id and r.vehicle_id == self.vehicle_id)
#                 e = record.filtered(
#                     lambda r: r.id != self.id and r.employee_id == self.employee_id and self.employee_id)
                if v:
                    raise ValidationError(_("You Need To Close Other Delegation Request for this Vehicle"))
#                 if e:
#                     raise ValidationError(_("You Need To Close Other Delegation Request for this Driver"))

    @api.onchange('start_date', 'end_date')
    @api.constrains('start_date', 'end_date')
    def check_data(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise UserError(_('Start Date must be less than or equal End Date '))

    @api.onchange('vehicle_id')
    def get_fleet_data(self):
        if self.vehicle_id:
            self.old_branch_id = self.vehicle_id.branch_id.id

    @api.onchange('employee_id')
    def get_emp_data(self):
        self.license_end = self.employee_id.license_end
        # self.vehicle_id.department_id = self.employee_id.department_id

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'
            if rec.driver_department:
               rec.vehicle_id.branch_id = rec.branch_id
               rec.vehicle_id.department_id = rec.driver_department.department_id
            elif rec.project_id:
                 rec.vehicle_id.project_id = rec.project_id

    def action_approve(self):
        for rec in self:
            rec.state = 'approve'

    def action_inprogress(self):
        for rec in self:
            # if rec.start_date > str(datetime.now().date()):
            #     raise ValidationError(_("You Can Start Request Early than Plan"))
            rec.state = 'in_progress'
            if rec.delegation_type == 'branch':
                rec.vehicle_id.old_branch_id = rec.vehicle_id.branch_id.id
                rec.vehicle_id.branch_id = rec.branch_id.id
            else:
                # rec.vehicle_id.partner_id = rec.employee_id.user_id.partner_id.id
                rec.vehicle_id.employee_id = rec.employee_id.id
                rec.employee_id.old_vehicle_id = rec.employee_id.vehicle_id.id
                rec.employee_id.vehicle_id = rec.vehicle_id.id
                rec.employee_id.delegation_start = rec.start_date
                rec.employee_id.delegation_end = rec.end_date
#                 rec.create_custody()

    def action_refuse(self):
        form_view_id = self.env.ref("odex_fleet.wizard_reject_reason_fleet_wiz_form").id
        return {
            'name': _("Reject Reason"),
           
            'view_mode': 'form',
            'res_model': 'reject.reason.fleet.wiz',
            'views': [(form_view_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_delegation_id': self.id},
        }

    def action_close(self):
        for rec in self:
            rec.state = 'close'
            if rec.delegation_type == 'branch':
                rec.vehicle_id.branch_id = rec.vehicle_id.old_branch_id.id
            else:
                rec.vehicle_id.owner_id = False
                rec.vehicle_id.employee_id = False
                rec.employee_id.vehicle_id = False
                rec.employee_id.delegation_start = False
                rec.employee_id.delegation_end = False
#                 if rec.custody_id:
#                     rec.custody_id.sudo().done()

    def action_cancel(self):
        for rec in self:
            rec.sudo().state = 'cancel'

    @api.model
    def delegation_expired_cron(self):
        date = datetime.now().date()
        delegation = self.company_id.delegation
        if delegation > 0:
            date = date + relativedelta(days=delegation)
            fleet = self.env['vehicle.delegation'].sudo().search(
                [('state', 'in', ['approve', 'in_progress']), ('end_date', '<=', str(date))])
            for f in fleet:
                template = self.env.ref('odex_fleet.delegation_expiration_email_template', False)
                template.send_mail(f.id)

    @api.model
    def delegation_start_cron(self):
        date = datetime.now().date()
        fleet = self.env['vehicle.delegation'].sudo().search(
            [('state', '=', 'approve'), ('start_date', '<=', str(date))])
        for f in fleet:
            f.action_inprogress()

    @api.model
    def delegation_close_cron(self):
        date = datetime.now().date()
        fleet = self.env['vehicle.delegation'].sudo().search(
            [('state', '=', 'in_progress'), ('end_date', '<=', str(date))])
        for f in fleet:
            f.action_close()
