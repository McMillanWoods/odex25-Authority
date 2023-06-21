from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class odex25_helpdeskSLA(models.Model):
    _inherit = "odex25_helpdesk.sla"

    category_id = fields.Many2one('service.category')
    service_id = fields.Many2one('helpdesk.service')



class ServiceCategory(models.Model):
    _name = 'service.category'
    _description = 'Service Category'

    name = fields.Char('Service Category', required=True)

    @api.constrains('name')
    def unique_service_category_constrains(self):
        if self.name:
            parties_party = self.env['service.category'].search([('name', '=', self.name), ('id', '!=', self.id)])
            if parties_party:
                raise ValidationError(_('The Service Category Must Be Unique'))


class HelpdeskService(models.Model):
    _name = 'helpdesk.service'
    _description = 'Helpdesk Service'

    name = fields.Char('Service', required=True)
    category_id = fields.Many2one('service.category')
    priority = fields.Selection([('0', 'All'), ('1', 'Low priority'), ('2', 'High priority'), ('3', 'Urgent')],
                                string='Priority', default='0')

    @api.constrains('name')
    def unique_helpdesk_service_constrains(self):
        if self.name:
            parties_party = self.env['helpdesk.service'].search([('name', '=', self.name), ('id', '!=', self.id)])
            if parties_party:
                raise ValidationError(_('The Helpdesk Service Must Be Unique'))
