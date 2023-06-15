from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class FleetMaintenance(models.Model):
    _name = 'fleet.maintenance'
    _description = 'Fleet Maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def default_get(self, default_fields):
        res = super(FleetMaintenance, self).default_get(default_fields)
        rec = self.env['fleet.account.config'].sudo().search([('type', '=', 'maintenance'), ('state', '=', 'confirm')],
                                                             limit=1)
        if rec:
            res['account_id'] = rec.account_id.id
            res['tax_id'] = rec.tax_id.id
        else:
            raise ValidationError(_("You Need To Configurate Account Details"))
        return res
    
    name = fields.Char(string="Name")
    next_request_date = fields.Date(string="Next Request Date")
    date = fields.Date(string=" Request Date", default=fields.Date.context_today)
    next_odometer = fields.Float(string="Next Odometer")
    odometer = fields.Float(string="Odometer")
    type = fields.Selection([('corrective', 'Corrective'), ('preventive', 'Preventive')], string='Maintenance Type', default="corrective")
    state = fields.Selection([('draft', 'Draft'), 
                              ('confirm', 'Confirm'),
                              ('approve', 'Approve'),
                              ('paid', 'Paid'),
                              ('refused', 'Refuse'),
                              ('cancel', 'Cancel'),
    ], string='state', default="draft")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    license_plate = fields.Char(required=True, related='vehicle_id.license_plate', store=True,
                                )
    employee_id = fields.Many2one('hr.employee', string="Driver" )
    quotation_ids = fields.One2many('fleet.quotation','request_id',string="Quotations")
    service_ids = fields.One2many('fleet.quotation.service','request_id',string="Quotations")
    branch_id = fields.Many2one('res.branch', string="Branch", default=lambda self: self.env.user.branch_id )
    # log_id = fields.Many2one('fleet.vehicle.log.services', string="Service Log")
    total_cost = fields.Float( string="Total Cost", compute="get_cost",store=True )
    total1 = fields.Float(string="Total",compute="get_total",store=True )
    account_id = fields.Many2one('account.account', string="Account")
    invoice_id = fields.Many2one('account.move', string="Invoice", copy=False)
    line_id = fields.Many2one('fleet.service.line.config', string="Line", copy=False)
    reason = fields.Text(string="Reject Reason",  tracking=True,)
    tax_id = fields.Many2one('account.tax', string='Tax', ondelete='restrict')
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)
    edit_access = fields.Boolean(compute="get_access",)

    def get_access(self):
        for rec in self:
            rec.edit_access = False
            if rec.state == 'approve' and  self.env.user.has_group('odex_fleet.fleet_group_account'):
                rec.edit_access = True

    @api.onchange('odometer')
    def onchange_odometer(self):
        for rec in self:
            if rec.odometer < rec.vehicle_id.odometer:
                if rec.env.user.lang == 'en_US':
                    raise ValidationError(_("odometer should be more than current odometer"))
                elif rec.env.user.lang == 'ar_SY' or rec.env.user.lang == 'ar_001':
                    raise ValidationError(_("عداد المسافات يجب أن يكون أكبر من عدادت المسافات الحالي"))

    @api.depends('service_ids')
    def get_total(self):
        for rec in self:
            if rec.service_ids:
                rec.total1 =  sum(rec.service_ids.mapped('qty'))


    def create_invoice(self):
        partner = self.quotation_ids.filtered(lambda r:r.approve == True).mapped('partner_id')
        if not partner:
            raise ValidationError(_("You NEED To ADD And Approve Quotation Lines"))
        amount = sum(self.quotation_ids.filtered(lambda r:r.approve == True).mapped('cost'))
        invoice = self.env['account.move'].sudo().create({
            'partner_id': partner[0].id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'name': 'Fleet Service Cost Invoice ',
            # 'account_id': partner[0].property_account_payable_id.id,
            'branch_id': self.vehicle_id.branch_id.id,
            'move_type': 'in_invoice',
            'invoice_date': datetime.now().today(),
        })

        self.env['account.move.line'].with_context(check_move_validity=False).sudo().create({
            'quantity': 1,
            'price_unit': amount,
            'move_id': invoice.id,
            'name': 'Maintenance Service Cost',
            'account_id': self.account_id.id,
            'tax_ids': [(6, 0, [self.tax_id.id])],

        })
        self.invoice_id = invoice.id
        # invoice.sudo().action_invoice_open()

    @api.depends('quotation_ids','quotation_ids.approve')
    def get_cost(self):
        for rec in self:
            if rec.quotation_ids.filtered(lambda r:r.approve == True):
                rec.total_cost = sum(rec.quotation_ids.filtered(lambda r:r.approve == True).mapped('cost'))

    @api.onchange('vehicle_id')
    def get_vehcile_date(self):
        if self.vehicle_id:
            self.odometer = self.vehicle_id.odometer
            self.employee_id = self.vehicle_id.employee_id.id
            self.branch_id = self.vehicle_id.branch_id.id

    def action_confirm(self):
        for rec in self:
            rec.sudo().state = 'confirm'

    def action_approve(self):
        for rec in self:
            record = rec.quotation_ids.sudo().filtered(lambda r: r.approve == True)
            if not record:
                raise ValidationError(_("You Need Approve Quotation First"))
            rec.state = 'approve'
            rec.vehicle_id.odometer = rec.odometer
            rec.vehicle_id.next_request_date = rec.next_request_date


    def action_refuse(self):
        for rec in self:
            rec.state = 'refused'


    def action_paid(self):
        for rec in self:
            rec.create_invoice()
            rec.state = 'paid'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

class FleetQuotation(models.Model):
    _name = 'fleet.quotation'
    _description = 'Fleet Quotation'

    cost = fields.Float(string="Cost")
    offer = fields.Binary(string="Offer Attachment")
    partner_id = fields.Many2one('res.partner',string="Partner")
    approve = fields.Boolean()
    request_id = fields.Many2one('fleet.maintenance' )
    reason = fields.Text(string="Reject Reason")
    state = fields.Selection(related='request_id.state',store=True)
    edit_access = fields.Boolean(compute="get_access", )

    def get_access(self):
        for rec in self:
            rec.edit_access = False
            if rec.state == 'approve' and self.env.user.has_group('odex_fleet.fleet_group_account'):
                rec.edit_access = True


    def action_approve(self):
        rec = self.request_id.quotation_ids.filtered(lambda r: r.approve)
        print("YYYYYYYYYYYY", rec)
        if rec:
            raise ValidationError(_("You Can Not Approve More Than One Quotation"))
        self.approve = True
        self.reason = False

    def action_reject(self):
        form_view_id = self.env.ref("odex_fleet.wizard_reject_reason_fleet_wiz_form").id
        return {
            'name': _("Reject Reason"),
           
            'view_mode': 'form',
            'res_model': 'reject.reason.fleet.wiz',
            'views': [(form_view_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_request_id': self.id},
        }

class FleetQuotationService(models.Model):
    _name = 'fleet.quotation.service'
    _description = 'Fleet Service'

    qty = fields.Float(string="Cost")
    cost = fields.Float(string="Cost")
    number = fields.Float(string="Number")
    total = fields.Float(string="Total", compute='_compute_total', readonly=True)
    service_id = fields.Many2one('fleet.service.type',string="Service")
    request_id = fields.Many2one('fleet.maintenance')

    @api.onchange('number', 'qty')
    def _compute_total(self):
        for r in self:
            r.total = r.number * r.qty



