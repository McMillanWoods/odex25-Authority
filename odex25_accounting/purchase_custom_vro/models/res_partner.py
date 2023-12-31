# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    
    vendor_list = fields.Selection(
        string='Vendor List',
        selection=[('white', 'White List'), ('black', 'Black List')]
    )
    
