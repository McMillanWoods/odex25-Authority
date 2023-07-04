# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    agreement_name = fields.Char()
    agreement_number = fields.Char()
    agreement_date = fields.Date()
    city = fields.Char()
