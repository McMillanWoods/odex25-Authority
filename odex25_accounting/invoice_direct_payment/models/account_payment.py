

from odoo import api, fields, models, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    name = fields.Char(readonly=True, copy=False, default='Draft')
    state = fields.Selection([('draft', 'Draft'), ('confirm_qc', 'QC Confirm'), ('confirm_fm', 'FM Confirm'),
                              ('check_lc', 'LC Check'), ('approve_gm', 'GM Approve'), ('approve_gs','GS Approve'),
                              ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled'),
                              ('cancelled', 'Cancelled')], track_visibility='onchange',readonly=True, default='draft',
                             copy=False, string="Status")
    gm_approve = fields.Boolean(string="GM Approval")
    gs_approve = fields.Boolean(string="GS Approval")
    description = fields.Text(string='Description')
    tracker_ids = fields.One2many('tracker', 'payment_id')

    def act_accountant(self):
        self.state = 'confirm_qc'
        if not self.name or self.name == 'Draft':
            # Use the right sequence to set the name
            if self.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if self.partner_type == 'customer':
                    if self.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if self.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if self.partner_type == 'supplier':
                    if self.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if self.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            self.name = self.env['ir.sequence'].with_context(ir_sequence_date=self.payment_date).next_by_code(sequence_code)
        # self.name = self.env['ir.sequence'].with_context(ir_sequence_date=self.payment_date).next_by_code('account.payment.supplier.invoice')
        self.tracker_ids.create({'payment_id':self.id, 'state':self.state})

    def act_confirm_qc(self):
        self.state = 'confirm_fm'
        self.tracker_ids.create({'payment_id':self.id, 'state':self.state})

    def act_confirm_fm(self):
        self.state = 'check_lc'
        self.tracker_ids.create({'payment_id':self.id, 'state':self.state})

    def act_check_lc(self):
        if self.gm_approve:
            self.state = 'approve_gm'
            self.tracker_ids.create({'payment_id': self.id, 'state': self.state})
        elif self.gs_approve:
            self.state = 'approve_gs'
            self.tracker_ids.create({'payment_id': self.id, 'state': self.state})
        else:
            self.post()


    def act_approve_gm(self):
        if self.gs_approve:
            self.state = 'approve_gs'
            self.tracker_ids.create({'payment_id':self.id, 'state':self.state})
        else:
            self.post()

    @api.multi
    def post(self):
        self.state = 'draft'
        # keep the name in case of a payment reset to draft
        for rec in self:
            if not rec.name or  rec.name == 'Draft':
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                    sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
        super(AccountPayment, self).post()
        self.tracker_ids.create({'payment_id':self.id, 'state':self.state})

    def action_draft(self):
        self.tracker_ids.unlink()
        return super(AccountPayment, self).action_draft()

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec['description'] = invoice['comment']
        return rec


class Tracker(models.Model):
    _name = "tracker"

    state = fields.Char()
    payment_id = fields.Many2one('account.payment')
    invoice_id = fields.Many2one('account.invoice')


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.constrains('iban')
    def check_iban(self):
        for rec in self:
            if rec.iban:
                if rec.iban[0].isalpha() and rec.iban[1].isalpha():
                    if rec.iban[0] == "S" and rec.iban[1] == "A":
                        if len(rec.iban) != 24:
                            raise Warning(_('Iban must be 24 digits'))
                    else:
                        if len(rec.iban) != 34:
                            raise Warning(_('Iban must be 34 digits'))

                else:
                    if len(rec.iban) != 34:
                        raise Warning(_('Iban must be 34 digits'))