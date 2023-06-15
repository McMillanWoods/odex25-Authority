# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'

    second_approve = fields.Integer(string='second approve')
    # third_approve = fields.Integer(string='third approve')
    purchase_budget = fields.Boolean(string='Purchase budget') 
    # purchase_analytic_account = fields.Many2one('account.analytic.account')


   
   