from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class FormRenew(models.Model):
    _name = 'form.renew'
    _description = 'Forn Renew'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def default_get(self, default_fields):
        res = super(FormRenew, self).default_get(default_fields)
        rec = self.env['fleet.account.config'].sudo().search([('type', '=', 'form'), ('state', '=', 'confirm')],
                                                             limit=1)
        if rec:
            res['account_id'] = rec.account_id.id
            res['tax_id'] = rec.tax_id.id
        else:
            raise ValidationError(_("You Need To Configurate Account Details"))
        return res

    name = fields.Char(string="Name")
    branch_id = fields.Many2one('res.branch', string="Branch")

    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm'),
                                        ('approve', 'Approved'),
                                        ('refused', 'Refused'),
                                        ('cancel', 'Cancel'),
                                       ], default='draft')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", )
    cost = fields.Float( string="Renew Cost", )
    date = fields.Date(string="Request Date",default=fields.Date.context_today)
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)
    end_date = fields.Date(string="End Date")
    new_date = fields.Date(string="New End Date")
    branch_id = fields.Many2one('res.branch', string="Branch", default=lambda self: self.env.user.branch_id)
    account_id = fields.Many2one('account.account', string="Account")
    invoice_id = fields.Many2one('account.move', string="Invoice", copy=False)
    partner_id = fields.Many2one('res.partner', string="Service Provider")
    tax_id = fields.Many2one('account.tax', string='Tax', ondelete='restrict')
    penalty_cost = fields.Float()
    edit_access = fields.Boolean(compute="get_access",)

    def get_access(self):
        for rec in self:
            rec.edit_access = False
            if rec.state == 'confirm' and  self.env.user.has_group('odex_fleet.fleet_group_account'):
                rec.edit_access = True


    @api.onchange('vehicle_id')
    def get_fleet_data(self):
        if self.vehicle_id:
            self.branch_id = self.vehicle_id.branch_id.id
            self.cost = self.vehicle_id.fleet_type_id.amount
            self.end_date = self.vehicle_id.form_end

    def create_invoice(self):
        invoice = self.env['account.move'].sudo().create({
            'partner_id': self.partner_id.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'name': 'Fleet Service Cost Invoice ',
            # 'account_id': self.partner_id.property_account_payable_id.id,
            'branch_id': self.vehicle_id.branch_id.id,
            'move_type': 'in_invoice',
            'invoice_date': datetime.now().today(),
        })

        self.env['account.move.line'].with_context(check_move_validity=False).sudo().create({
            'quantity': 1,
            'price_unit': self.cost+self.penalty_cost,
            'move_id': invoice.id,
            'name': 'Fleet Form Renew Cost',
            'account_id': self.account_id.id,
            'tax_ids': [(6, 0, [self.tax_id.id])],

        })
        self.invoice_id = invoice.id
        # invoice.sudo().action_invoice_open()

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_approve(self):
        for rec in self:
            rec.vehicle_id.form_end = self.new_date
            rec.state = 'approve'
            rec.create_invoice()

    def action_refuse(self):
        for rec in self:
            rec.state = 'refused'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

