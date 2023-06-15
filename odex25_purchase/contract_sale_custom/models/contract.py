
from odoo import api, fields, models, _


class ContractContract(models.Model):
    _inherit = 'contract.contract'
    sale_order = fields.Many2one('sale.order', string="Sale Order")
