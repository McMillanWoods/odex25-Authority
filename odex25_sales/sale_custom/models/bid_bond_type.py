# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BidBondType(models.Model):
    _name = 'bid.bond.type'
    _description = 'Bid Bond Type'

    name = fields.Char('Name', required=True)
    ceo_approve = fields.Boolean('CEO Approved')