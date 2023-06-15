# -*- coding: utf-8 -*-

from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ContractInstallmentLine(models.Model):
    _name = 'line.contract.installment'
    _description = "Installment"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Installment Name', required=True)
    amount = fields.Monetary(string='Amount')
    tax_id = fields.Many2many(comodel_name='account.tax', string='Taxes')

    tax_amount = fields.Float(compute='_compute_amount_tax',
                              string='Tax Amount',
                              readonly=True,
                              store=True)

    total_amount = fields.Float(compute='_compute_total_amount',
                                store=True, string='Amount With Tax',
                                readonly=True)

    due_date = fields.Date(string='Due Date', index=True, required=True)
    state = fields.Selection([('not_invoiced', 'Not Invoiced'),
                              ('invoiced', 'Invoiced'),
                              ('paid', 'Paid'), ('cancel', 'Cancel')], string="Status", default="not_invoiced")
    invoice_id = fields.Many2one(comodel_name='account.move', string='Invoice', readonly=True)
    invoice_is_paid = fields.Boolean(compute='_compute_invoice_state')
    account_id = fields.Many2one(comodel_name='account.account', string='Account')
    contract_id = fields.Many2one('contract.contract', string='Contract', ondelete='restrict',
                                  index=True,)
    installment_type = fields.Selection(string='Type', selection=[('percent', 'Percent'), ('fixed', 'Fixed')],
                                        default="fixed", required=True)
    percent = fields.Integer(string='Percent')
    partner_id = fields.Many2one(
        string='partner', index=True,
        comodel_name='res.partner', readonly=True, related="contract_id.partner_id"
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company', readonly=True, related="contract_id.company_id"
    )
    user_id = fields.Many2one(
        'res.users', string='User',
        readonly=True, related="contract_id.user_id",
        copy=False)

    currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Currency",
        readonly=True,
    )

    date_planned_start = fields.Datetime(string='Scheduled Date Start')
    date_planned_finished = fields.Datetime(string='Scheduled Date Finished')
    description = fields.Text(string="Description")
    taxed_invoice = fields.Selection([('taxed_invoice', 'Taxed Invoice'),
                                      ('final_invoice', 'Final invoice (reconciliation  advance payment and tax )'),
                                      ('with_invoice', 'Advance (with Invoice)'),
                                      ('without_invoice', 'Advance (without invoice)')], string=" Taxed Invoice",
                                     default="taxed_invoice")
    payment_id = fields.Many2one(
        string='Payment',
        comodel_name='account.payment',

    )

    journal_id = fields.Many2one(
        string='journal',
        comodel_name='account.journal',

    )
    contract_type = fields.Selection(string='Payment Type',related="contract_id.contract_type")
    

    def num_to_letter(self, number):
        num_to_word = self.env['odex.num']
        numb_arbic = num_to_word.convertNumber(number)
        last_arbic_number = numb_arbic.replace('فاصل', 'و')
        return last_arbic_number

    @api.onchange('taxed_invoice')
    def onchange_taxed_invoice(self):
        if  self.taxed_invoice == 'final_invoice':
            self.amount = self.contract_id.remaining_amount
# domain="[('internal_type','in', ('payable','receivable')), ('deprecated', '=', False)]
        # """change the domain of account_id  whenever the user changes the selected value."""
        # if self.taxed_invoice == 'taxed_invoice' or self.taxed_invoice == 'final_invoice' or self.taxed_invoice == 'without_invoice':
        #     # change type to income ,return id from xml data ref
        #     if self.contract_id.contract_type == 'purchase':
        #         return {
        #         'domain': {'account_id': [('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id)]}}
        #     elif self.contract_id.contract_type == 'sale':
        #         return {
        #             'domain': {'account_id': [('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id)]}}

        # if self.taxed_invoice == 'with_invoice':
        #     # change type to prepayments ,return id from xml data ref
        #     return {'domain': {
        #         'account_id': [('user_type_id', '=', self.env.ref('account.data_account_type_prepayments').id)]}}

    
    def change_state_to_invoiced(self):
        invoice_type = ''
        customer_invoice_lines = []

        if self.amount <= 0:
            raise ValidationError(_('You Cant Create Invoice With Amout Zero Or Less'))
        if not self.contract_id:
            raise ValidationError(_('you cant create invoice without contract'))

        if self.contract_id.type == 'sale':
            invoice_type = 'out_invoice'
        elif self.contract_id.type == 'purchase':
            invoice_type = 'in_invoice'

        # if conditions to create invoice lines base taxed_invoice field

        if self.taxed_invoice == 'with_invoice' or self.taxed_invoice == 'taxed_invoice':
            customer_invoice_lines = [(0, 0, {
                'name': self.name,
                'account_id': self.account_id.id,
                'quantity': 1.0,
                'price_unit': self.amount,
                'tax_ids': [(6, 0, self.tax_id.ids)] if self.tax_id else False,

            })]

        if self.taxed_invoice == 'final_invoice':
            # beging with add this inovice lines to create the invoice
            customer_invoice_lines.append(
                (0, 0, {
                    'name': self.name,
                    'account_id': self.account_id.id,
                    'quantity': 1.0,
                    'price_unit': self.amount,
                    'tax_ids': [(6, 0, self.tax_id.ids)] if self.tax_id else False,

                }))
            # then search for the related invoices to this contract ,
            # combine the above invoice line with below lines to create one invoce. 
            contract_invoices = self.env['account.move'].search([('contract_id', '=', self.contract_id.id),])
            # ('taxed_invoice', '=', 'without_invoice')
            for contract in contract_invoices:
                for inv in contract.invoice_line_ids:
                    customer_invoice_lines.append((0, 0, {
                        'name': inv.name,
                        'account_id': inv.account_id.id,
                        'quantity': -1,
                        'price_unit': inv.price_unit,
                        'tax_ids': [(6, 0, inv.tax_ids.ids)] if inv.tax_ids else False,

                    }))

        # create payment if tax invoice = without invoice,no invoice will be created
        if self.taxed_invoice == 'without_invoice':
            # prepare payment vals in case of tax_invoice ==without_invoice
            payment_vals = {
                'reconciled_invoice_ids': [],
                'reconciled_bill_ids': [],  # for related invoice,to do :fix this to add inovice related to this payment
                'amount': self.total_amount,
                'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,  # note
                'partner_id': self.contract_id.partner_id.id,
                'payment_date': fields.Date.today(),
                'partner_type': 'customer',
                'payment_type': 'inbound',
                'currency_id': self.currency_id.id,
                'journal_id': self.journal_id.id,
                'contract_id': self.contract_id.id,

            }
            payment = self.env['account.payment'].create(payment_vals)
            move = self.env['account.move'].create({
                'name': '/',
                'journal_id': 3,
                # 3 is the id of missilionous journal, to do:fix this if you want to make journal dynamic
                'date': payment.payment_date,
                'line_ids': [(0, 0, {
                    'payment_id': payment.id,
                    'partner_id': self.contract_id.partner_id.id,
                    'debit': self.total_amount,
                    'account_id': self.contract_id.partner_id.property_account_receivable_id.id,
                }), (0, 0, {
                    'payment_id': payment.id,
                    'partner_id': self.contract_id.partner_id.id,
                    'credit': self.total_amount,
                    'account_id': self.account_id.id,
                })]
            })
            move.post()
            self.write({
                'payment_id': payment.id if payment.id else payment.journal_id.id,
                'state': 'paid'
            })

        # second create the invoice wiht customer_invoice_lines list, if the tax invoice != without invoice
        if not self.taxed_invoice == 'without_invoice':
            invoice = self.env['account.move'].create({
                'partner_id': self.contract_id.partner_id.id,
                'invoice_line_ids': customer_invoice_lines,
                'invoice_date': self.due_date,
                'move_type': 'out_invoice' if self.contract_type == 'sale' else 'in_invoice',
                'contract_id': self.contract_id.id,
                # 'reference' : "%s - %s" %(self.contract_id.name,self.name) ,
            })
            self.write({
                'invoice_id': invoice.id,
                'state': 'invoiced'
            })

    
    @api.depends('invoice_id.state')
    def _compute_invoice_state(self):
        if self.invoice_id.state == 'paid':
            self.invoice_is_paid = True
        if self.invoice_is_paid is True:
            self.write({'state': 'paid'})

    
    def cancel_state(self):
        self.write({'state': 'cancel'})

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        if self.contract_id and self.contract_id.total_amount <= 0:
            self.contract_id = False
            raise ValidationError(_("Contract total amount is zero hence you can't create installment for it!"))
    @api.onchange('amount')
    def onchange_total_amount(self):
        installments = sum(self.search([('contract_id','=',self.contract_id.id)]).mapped('total_amount'))
        if self.total_amount > self.contract_id.with_tax_amount - installments:
            raise ValidationError(_("the amount can't be greater than contract remaining amount!"))
    
    @api.constrains('contract_id')
    def amount_contract(self):
        
        if self.contract_id and self.contract_id.state == 'in_progress':
            raise ValidationError(_('This Contract Is In Progress State You Cant New Installments'))
        
       
        
            
            
        
    @api.constrains('taxed_invoice')
    def constrians_taxed_invoice(self):
        if self.search_count([('contract_id','=',self.contract_id.id),('taxed_invoice','=','final_invoice')]) > 1:
            raise ValidationError(_('This Contract already has final installment'))
    
    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("the amount can't be zero or less"))
            

    
    @api.constrains('percent')
    def _check_percent(self):
        if self.installment_type == 'percent' and self.percent <= 0 and self.taxed_invoice != 'final_invoice' :
            raise ValidationError(_("the percent must be zero or less"))

    @api.onchange('percent', 'installment_type', 'contract_id','taxed_invoice')
    def _onchange_installment_type(self):
        amount = 0
        # this method is triggered to calculate amount when one of fields in decorator  change in view
        for rec in self:
            if rec.percent > 0:
                rec.amount = rec.contract_id.total_amount * rec.percent / 100
            # rec.write({'amount':amount})

            # update installment amount fields with contract amount fields because its final invoice.
            if rec.taxed_invoice == 'final_invoice':
                if rec.contract_id:
                    # invoices = self.env['account.move'].search([('contract_id', '=', self.contract_id.id)]).ids
                    installments = self.search([('contract_id', '=', self.contract_id.id),('taxed_invoice', 'in', ['taxed_invoice','with_invoice']),('state','=','invoiced')])
                    amount = sum(installments.mapped('amount'))
                    if amount:
                        rec.amount = rec.contract_id.total_amount - amount
                    # rec.amount = rec.contract_id.total_amount
                    # rec.tax_id = rec.contract_id.tax_id if rec.contract_id.tax_id else False
                    # rec.tax_amount = rec.contract_id.tax_amount
                    # rec.total_amount = rec.contract_id.with_tax_amount

    
    @api.depends('tax_id', 'amount')
    def _compute_amount_tax(self):
        self.tax_amount =0
        for rec in self:
            if rec.tax_id:
                taxes = [tax._compute_amount(rec.amount, rec.amount) for tax in self.tax_id]
                rec.tax_amount = sum(taxes)

    
    @api.depends('tax_amount', 'amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.amount + rec.tax_amount

    @api.model
    def send_contract_email(self):

        # add 30 day to the day the cron running to compare with due date
        the_day = date.today() + timedelta(days=30)

        installments = self.search([('due_date', '=', the_day), ('state', '=', 'not_invoiced')])

        template = self.env.ref('contract.contract_installment_email_template')

        for installment in installments:
            # change email_to in the template depending on installment responsible
            template.email_to = installment.contract_id.user_id.email
            template.send_mail(installment.id, force_send=True)

    @api.model
    def send_daily_installment_email(self):

        # get current date
        due_day = date.today()

        installments = self.search([('due_date', '=', due_day), ('state', '=', 'not_invoiced')])

        template = self.env.ref('contract.daily_installment_email_template')
        for installment in installments:
            # change email_to in the template depending on installment responsible
            template.email_to = installment.contract_id.user_id.email
            template.send_mail(installment.id, force_send=True)

    @api.model
    def create(self, values):
       
        contract = values.get( 'contract_id',False)
        if contract:
            contract_id = self.env['contract.contract'].browse(contract)
            if contract_id.state == 'closed':
                raise ValidationError(_("Contract is closed you cant create installments for it!"))
        result = super(ContractInstallmentLine, self).create(values)

        return result

    
    def unlink(self):
        invoiced = self.filtered(lambda rec: rec.state != 'not_invoiced')
        if invoiced:
            raise ValidationError(_("Delete Operation Cannot be Done Because on or more installment  has been invoiced") %())
        else:
            return super(ContractInstallmentLine,  self).unlink()
