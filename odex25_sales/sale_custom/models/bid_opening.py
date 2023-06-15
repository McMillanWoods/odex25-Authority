# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BidOpeing(models.Model):
    _name = 'bid.opening'
    _description = 'Bid Opeing'
    _rec_name = 'competitor_id'

    competitor_id = fields.Many2one('competitor', 'Competitor')
    amount = fields.Float('Amount')
    rank = fields.Integer('Rank')
    sale_order_id = fields.Many2one('sale.order', string='Proposal', required=True, ondelete='cascade', index=True, copy=False)



class Competitor(models.Model):
    _name = 'competitor'
    _description = 'Competitor'

    name = fields.Char('Name')
