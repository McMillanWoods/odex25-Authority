from odoo import api, fields, models ,_
from odoo.exceptions import ValidationError


class PortalResUser(models.Model):
    _inherit = 'res.users'

    is_customer_support = fields.Boolean(string='Customer Support?', default=False)
 
