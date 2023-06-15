# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sector_id = fields.Many2one('sector', 'Sector')


class ResPartnerIndustry(models.Model):
    _inherit = "res.partner.industry"

    parent_id = fields.Many2one('res.partner.industry', string='Parent industry')

