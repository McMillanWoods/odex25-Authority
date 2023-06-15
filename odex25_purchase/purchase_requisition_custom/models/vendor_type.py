from odoo import api, fields, models

class VendorTypes(models.Model):
    _name = 'vendor.type'
    _description = 'vendor.type'

    name = fields.Char('Name',required=True)
