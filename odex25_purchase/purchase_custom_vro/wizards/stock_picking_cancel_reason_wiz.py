from odoo import models, fields, api, _


class StockPickingCancelReasonWiz(models.TransientModel):
    _name = "stock.picking.cancel.reason.wiz"

    cancel_reason = fields.Char("Cancel Reason", required=1)

    def confirm(self):
        active_id = self._context.get('active_id')
        picking = self.env["stock.picking"].browse(active_id)
        picking.cancel_reason = self.cancel_reason
        # Change Request
        if picking.state == 'assigned':
            picking.cancelled_by_employee = True
            picking.state = 'confirm'
        else:
            picking.action_cancel_super()
        picking.message_post(self.cancel_reason)
