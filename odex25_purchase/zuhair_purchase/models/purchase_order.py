

from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    category_ids = fields.Many2many('product.category',string="categories")

    def cancel_order(self):
        for rec in self:
            rec.state = 'draft'

    def to_Cancel(self):
        for rec in self:
            rec.state = 'cancel'

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id_category(self):
        if self.order_id.category_ids:
            products = self.env['product.product'].search([('categ_id','in',self.order_id.category_ids.ids)])
            res = {'domain':{'product_id':[('id','in',products.ids)]}}
            return res
class ResPartner(models.Model):
    _inherit = 'res.partner'

    type = fields.Selection(selection_add=[('supplier account manager', 'Supplier Account Manager')], ondelete={'code': 'cascade'})