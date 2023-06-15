# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EvaluationCriteria(models.Model):
    _name = 'evaluation.criteria'
    _description = 'Rvaluatioin Creiteria'

    active = fields.Boolean(string='active',default=True)
    vendor_type = fields.Many2one(comodel_name='vendor.type', string='Vendor Type')
    name = fields.Char(string='Name')
    owner = fields.Selection([
        ('account', 'Finance'),
        ('purchase' , 'Purchase'),
        ('stock' , 'Stock'),
    ], string='Owner')
    
    @api.model_create_multi
    def create(self, vals_list):
        res_ids = super(EvaluationCriteria, self).create(vals_list)
        return res_ids





    
    
    

    