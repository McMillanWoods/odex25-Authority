from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    government_type = fields.Selection(string="Governmental Type",
                                       selection=[('gov', 'Governmental'), ('not_gov', 'Non-Governmental')],
                                       required=False, )
