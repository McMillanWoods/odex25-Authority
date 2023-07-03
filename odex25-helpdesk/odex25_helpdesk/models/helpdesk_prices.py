# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class HelpDeskPrice(models.Model):
    _name = 'helpdesk.price'
    _description = 'Helpdesk Price'

    name = fields.Char(string="Title", required="True")
    recurrency = fields.Selection([('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)'), ('yearly', 'Year(s)')],
            string='Plan', help="Invoice automatically repeat at specified interval", required=True, default='monthly')
    amount = fields.Float(string="Price", required="True")
    tax_id = fields.Many2one(comodel_name='account.tax', string='Taxes')

    tax_amount = fields.Float(compute='_compute_amount_tax',
                              string='Tax Amount',
                              readonly=True,
                              store=True)

    total_amount = fields.Float(compute='_compute_total_amount',
                                store=True, string='Amount With Tax',
                                readonly=True)
    company_id = fields.Many2one('res.company', string="Company", required="True", default=lambda self: self.env.user.company_id)
    is_active = fields.Boolean('Publish for Customer?', default=True)
    description = fields.Text()

    @api.depends('tax_id', 'amount')
    def _compute_amount_tax(self):
        for rec in self:
            rec.tax_amount = 0
            if rec.tax_id:
                taxes = [tax._compute_amount(rec.amount, rec.amount) for tax in rec.tax_id]
                rec.tax_amount = sum(taxes)

    @api.depends('tax_amount', 'amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.amount + rec.tax_amount
