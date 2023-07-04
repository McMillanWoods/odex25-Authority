from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class odex25_helpdeskTeam(models.Model):
    _inherit = "odex25_helpdesk.team"

    is_internal_team = fields.Boolean('Internal Team', default=False)

class odex25_helpdeskSLA(models.Model):
    _inherit = "odex25_helpdesk.sla"

    category_id = fields.Many2one('service.category')
    service_id = fields.Many2one('helpdesk.service')




#
# class odex25_helpdeskTicket(models.Model):
#     _inherit = 'odex25_helpdesk.ticket'
#
#     service_id = fields.Many2one('helpdesk.service')
#     category_id = fields.Many2one('service.category')
#     employee_id = fields.Many2one('hr.employee', 'Employee Id',
#                                   default=lambda item: item.get_user_id(), index=True)
#     work_email = fields.Char(related='employee_id.work_email')
#     work_location = fields.Char(related='employee_id.work_location')
#     department_id = fields.Many2one(related='employee_id.department_id')
#     deb_name = fields.Char(related='department_id.name')
#     division_id = fields.Many2one(related='department_id.parent_id',string="Division")
#     project_no = fields.Char("Project Number")
#     transform_no = fields.Char("Transform Number")
#
#     def get_user_id(self):
#         employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
#         if employee_id:
#             return employee_id.id
#         else:
#             return False
class ServiceCategory(models.Model):
    _name = 'service.category'

    name = fields.Char('Service Category', required=True)

    @api.constrains('name')
    def unique_service_category_constrains(self):
        if self.name:
            parties_party = self.env['service.category'].search([('name', '=', self.name), ('id', '!=', self.id)])
            if parties_party:
                raise ValidationError(_('The Service Category Must Be Unique'))


class HelpdeskService(models.Model):
    _name = 'helpdesk.service'

    name = fields.Char('Service', required=True)
    category_id = fields.Many2one('service.category')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
    ], default='0', index=True, string="Priority")

    @api.constrains('name')
    def unique_helpdesk_service_constrains(self):
        if self.name:
            parties_party = self.env['helpdesk.service'].search([('name', '=', self.name), ('id', '!=', self.id)])
            if parties_party:
                raise ValidationError(_('The Helpdesk Service Must Be Unique'))
