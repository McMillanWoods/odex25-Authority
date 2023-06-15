from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class Infractions(models.Model):
    _name = 'vehicle.infraction'
    _description = 'Vehicle Infraction'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", )
    branch_id = fields.Many2one('res.branch', string="Branch")
    old_branch_id = fields.Many2one('res.branch', string="Old Branch")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    vin_sn = fields.Char('Chassis Number', related='vehicle_id.vin_sn', store=True,
                         copy=False)
    model_id = fields.Many2one('fleet.vehicle.model', 'Model', related='vehicle_id.model_id', store=True, )
    license_plate = fields.Char(required=True, related='vehicle_id.license_plate', store=True)
    serial_number = fields.Char(related='vehicle_id.serial_number', string="Serial Number")
    fleet_type_id = fields.Many2one('fleet.type', string="Fleet Type", related='vehicle_id.fleet_type_id', store=True, )
    employee_id = fields.Many2one('hr.employee', string="Driver",
                                  domain="[('driver', '=', True),('vehicle_id', '=', False)]")
    license_number = fields.Char(string="License Number", related='employee_id.license_number', store=True)
    license_end = fields.Date(string="License End")
    reason = fields.Text()
    infraction_type = fields.Selection(selection=[('accident', 'Accident'),
                                        ('infraction', 'Infraction'),],string="Infraction Type")
    infraction_number = fields.Char(string="Infraction Number")
    infraction_date = fields.Date(string="Infraction Date")
    infraction_cost = fields.Integer(string="Infraction Cost")
    cost_percentage = fields.Integer(string="Cost Percentage%")
    discount_amount = fields.Integer(string="Discount Amount", compute = "get_discount_amount", store = True)
    benefits_discounts = fields.Many2one(comodel_name='hr.salary.rule', string='Benefits/Discounts')
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm'),
                                        ('approve', 'Approved'),
                                        ('in_progress', 'In Progress'),
                                        ('refused', 'Refused'),
                                        ('cancel', 'Cancel')], default='draft')
    advantage_id = fields.Many2one(comodel_name='contract.advantage', string='Deduction Employee')

    @api.depends('infraction_cost', 'cost_percentage')
    def get_discount_amount(self):
        for rec in self:
            if rec.cost_percentage > 0 :
                rec.discount_amount = rec.infraction_cost * rec.cost_percentage
            else :
                rec.discount_amount = rec.infraction_cost
            # print(rec.discount_amount)

    @api.onchange('start_date', 'end_date')
    @api.constrains('start_date', 'end_date')
    def check_data(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise UserError(_('Start Date must be less than or equal End Date '))

    @api.onchange('vehicle_id')
    def get_fleet_data(self):
        if self.vehicle_id:
            self.old_branch_id = self.vehicle_id.branch_id.id
            self.employee_id = self.vehicle_id.employee_id
            self.license_number = self.vehicle_id.employee_id.license_number
            self.license_end = self.vehicle_id.employee_id.license_end

    @api.onchange('employee_id')
    def get_emp_data(self):
        self.license_end = self.employee_id.license_end

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_approve(self):
        for rec in self:
            rec.state = 'approve'

    def action_inprogress(self):
        for rec in self:
            rec.state = 'in_progress'
            contract_move_id = rec.env['contract.advantage'].create({
                'benefits_discounts': rec.benefits_discounts.id,
                'date_from': rec.start_date,
                'date_to': rec.end_date,
                'type': 'customize',
                'amount' : rec.discount_amount,
                'employee_id': rec.employee_id.id,
                'contract_advantage_id': rec.employee_id.contract_id.id,
                'penalty_id': True,
                'out_rule': True,
                'state': 'draft',
            })
            rec.advantage_id = contract_move_id.id

    def action_refuse(self):
        form_view_id = self.env.ref("odex_fleet.wizard_reject_reason_infraction_form").id
        return {
            'name': _("Reject Reason"),

            'view_mode': 'form',
            'res_model': 'reject.reason.infraction.wiz',
            'views': [(form_view_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_infraction_id': self.id},
        }

    def action_cancel(self):
        for rec in self:
            rec.sudo().state = 'cancel'