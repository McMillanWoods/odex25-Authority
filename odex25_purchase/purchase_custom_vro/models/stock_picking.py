# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    cancel_reason = fields.Char("Cancel Reason")
    state = fields.Selection(selection_add=[('confirm', 'Confirm')])
    product_type = fields.Selection(selection=[('material', 'Material'), ('service', 'Service')])
    cancelled_by_employee = fields.Boolean("Cancelled By Employee")

    def button_confirm(self):
        self.state = 'confirm'
        self.cancelled_by_employee = False
        for rec in self:
            count = 0
            for line in rec.move_lines:
                if not (line.quantity_done == 0 and line.product_uom_qty == 0):
                    if line.quantity_done > line.product_uom_qty:
                        raise ValidationError(
                            _("It is not possible to receive a larger quantity than the requested quantity"))
                    # if line.quantity_done  <=0:
                    #     raise ValidationError(_("It is not possible to receive Zero or less than Zero Qty"))
                    # Change Request
                    if line.quantity_done < 0:
                        raise ValidationError(_("It is not possible to receive Zero or less than Zero Qty"))
                    if line.quantity_done == 0:
                        count += 1
            if count == len(rec.move_lines):
                raise ValidationError(_("Sorry, at least one item must be received"))

    # Change Request
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        pickings = self.env['stock.picking'].search([('state', '=', 'done'), ('purchase_id', '=', self.purchase_id.id)])
        pickings_not_c = self.env['stock.picking'].search(
            [('state', '!=', 'cancel'), ('purchase_id', '=', self.purchase_id.id)])
        done = True
        for pik in pickings:
            for line in pik.move_lines:
                if line.quantity_done != line.product_uom_qty:
                    done = True
        if len(pickings) != len(pickings_not_c):
            done = False
        if done:
            if self.purchase_id.request_id:
                self.purchase_id.request_id.write({
                    'state': 'done'
                })

        return res

    def send_to_employee(self):
        self.state = 'assigned'

    def action_cancel_super(self):
        # we need to change later  ,not ido this code casue i found the logic of inhirtance its not rghite so
        pickings = self.env['stock.picking'].search([('state', '=', 'done'), ('purchase_id', '=', self.purchase_id.id)])
        pickings_not_c = self.env['stock.picking'].search(
            [('state', '!=', 'cancel'), ('purchase_id', '=', self.purchase_id.id)])
        if len(pickings) != len(pickings_not_c):
            if self.purchase_id.request_id:
                self.purchase_id.request_id.write({
                    'state': 'done'
                })

        return super(StockPicking, self).action_cancel()

    def action_cancel(self):
        # if self.cancel_reason == "" or self.cancel_reason is False:
        #     view_id = self.env.ref('purchase_custom_vro.wizard_picking_cancel_reason_view_form').id
        #     return {
        #         'type': 'ir.actions.act_window',
        #         'name': _('Cancellation Reason'),
        #         'res_model': 'stock.picking.cancel.reason.wiz',
        #         'view_type': 'form',
        #         'view_mode': 'form',
        #         'views': [(view_id, 'form')],
        #         'target': 'new',
        #     }
        # else:
        #     return super(StockPicking, self).action_cancel()
        # Change Request
        # if self.cancel_reason == "" or self.cancel_reason is False:
        view_id = self.env.ref('purchase_custom_vro.wizard_picking_cancel_reason_view_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cancellation Reason'),
            'res_model': 'stock.picking.cancel.reason.wiz',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
        }

        # else:
        #     return super(StockPicking, self).action_cancel()

    def unlink(self):
        if self.state == 'done':
            raise UserError(_("You cannot delete a done delivery!"))
        else:
            return super(StockPicking, self).unlink()


class StockMove(models.Model):
    _inherit = "stock.move"

    note = fields.Char()

    # #need more invistgate in this lines , to be sure about qty done , temp situation
    # @api.constrains('quantity_done','product_uom_qty')
    # def quantity_done_with_product_uom_qty_constrains(self):
    #     print ("------ quantity_done_with_product_uom_qty_constrains")
    #     for rec in self :
    #         if rec.quantity_done > rec.product_uom_qty:
    #             raise ValidationError(_("It is not possible to receive a larger quantity than the requested quantity"))
    #         if rec.quantity_done  <=0:
    #             raise ValidationError(_("It is not possible to receive Zero or less than Zero"))


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    in_entire_package = fields.Boolean(compute='_compute_in_entire_package')

    def _compute_in_entire_package(self):
        """ This method check if the move line is in an entire pack shown in the picking."""
        for ml in self:
            picking_id = ml.picking_id
            ml.in_entire_package = picking_id and picking_id.picking_type_entire_packs and picking_id.state != 'done'\
                                   and ml.result_package_id and ml.result_package_id in picking_id.entire_package_ids
