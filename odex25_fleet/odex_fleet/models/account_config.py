from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AccountConfigFleet(models.Model):
    _name = 'fleet.account.config'
    _description = 'Fleet Cost'

    name = fields.Char(string="Name")
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm'),
                                        ('close', 'Close')
                                        ],default='draft')
    type = fields.Selection(selection=[('fuel', 'Fuel'),
                                        ('service', 'Service'),
                                        ('form', 'Form'),
                                        ('maintenance', 'Maintenance'),
                                       ],)
    account_id = fields.Many2one('account.account', string="Account")
    tax_id = fields.Many2one('account.tax', string='Tax', ondelete='restrict')


    def action_confirm(self):
        rec = self.env['fleet.account.config'].sudo().search([('id','!=',self.id),('type','=',self.type),('state','=','confirm')])
        if rec:
            raise ValidationError(_("You can not Have More than one Confirm record "))
        self.state = 'confirm'

    def action_close(self):
        self.state = 'close'