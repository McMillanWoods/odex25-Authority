from odoo import models, fields, api, _


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    picking_ids = fields.One2many("stock.picking", compute="_compute_picking_ids")
    purchase_order_ids = fields.One2many("purchase.order", "request_id")
    picking_count = fields.Integer(compute='_compute_picking_ids',
                                   string='Deliveries',  compute_sudo=True)
    
    Suggest_vendors = fields.Text(
        string='Suggest Vendors',
    )
    
    @api.multi
    def _compute_picking_ids(self):
        for rec in self:
            if len(rec.purchase_order_ids):
                rec.picking_ids = rec.purchase_order_ids.mapped('picking_ids')
                count = len(rec.purchase_order_ids.mapped('picking_ids'))
                rec.picking_count = count
                rec.write({'picking_count':count})

    @api.multi
    def action_view_picking(self):
        action = self.env.ref('purchase_custom_vro.action_picking_tree_incoming')
        result = action.read()[0]
        result['context'] = {}
        pick_ids = self.mapped('picking_ids')
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('purchase_custom_vro.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result
