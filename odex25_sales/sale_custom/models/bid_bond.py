# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BidBond(models.Model):
    _name = 'bid.bond'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Bid Bond'

    name = fields.Text('Description', required=True, translate=True, tracking=True)
    sale_order_id = fields.Many2one('sale.order', 'Proposal')
    bidbond_type = fields.Many2one('bid.bond.type', 'Bid Bond Type', tracking=True)
    ceo_approve = fields.Boolean(related='bidbond_type.ceo_approve', store=True)
    bidbond_date = fields.Date('Bid Bond Date', tracking=True)
    bidbond_amount = fields.Float('Bid Bond Amount', tracking=True)
    expiry_date = fields.Date('Expirey Date')
    partner_id = fields.Many2one('res.partner', 'Client')
    contract_amount = fields.Float('Contract Amount', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('send', 'Send'),
                              ('confirm', 'Confirmed'), 
                              ('ceo_approve', 'CEO Approved'), 
                              ('approve', 'Approved')],  string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    lg_percent = fields.Float('LG%')
    project_country_id = fields.Many2one(related="sale_order_id.project_country_id", store=True)
    project_state_id = fields.Many2one(related="sale_order_id.project_state_id", store=True)
    city_id = fields.Many2one(related="sale_order_id.city_id", store=True)

    customer_country_id = fields.Many2one(related="partner_id.country_id", store=True)
    customer_state_id = fields.Many2one(related="partner_id.state_id", store=True)
    lg_request = fields.Selection([('draft','Draft'), ('extention', 'Extention'), ('cancel', 'Cancel')])
    bidbond_id = fields.Many2one('bid.bond', 'BidBond Extention')


    def action_send(self):

        self.state = 'send'


    def action_confirm(self):

        self.state = 'confirm'


    def action_approve(self):
        """ create payment """
        self.state = 'approve'


    def action_ceo_approve(self):

        self.state = 'ceo_approve'



    @api.onchange('sale_order_id')
    def onchange_sale_order_id(self):

        if self.sale_order_id:

            self.contract_amount = self.sale_order_id.amount_total
