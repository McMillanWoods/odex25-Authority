# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def mail_purchase_order_on_send(self):
        res = super().mail_purchase_order_on_send()
        if self._context.get('purchase_mark_rfq_sent'):
            order = self.env['purchase.order'].browse(self._context['default_res_id'])
            order.state = 'draft'
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    product_type = fields.Selection(selection=[('material', 'Material'), ('service', 'Service')])

    def action_cancel(self):
        self.state = 'cancel'
        self.requisition_id.with_context({'cancel_employee_request': True}).action_cancel()

    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]

        # override the context to get rid of the default filtering on operation type
        result['context'] = {}
        pick_ids = self.mapped('picking_ids')
        # choose the view_mode accordingly
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result

    def action_view_purchase_request(self):
        action = self.env.ref('purchase_requisition_custom.purchase_request_action')
        result = action.read()[0]
        result['context'] = {}
        res = self.env.ref('purchase_requisition_custom.purchase_request_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = self.request_id.id
        return result

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id
        currency = partner.property_purchase_currency_id or requisition.company_id.currency_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.get_fiscal_position(partner.id)
        fpos = FiscalPosition.browse(fpos)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id
        self.company_id = requisition.company_id.id
        self.currency_id = currency.id
        if not self.origin or requisition.name not in self.origin.split(', '):
            if self.origin:
                if requisition.name:
                    self.origin = self.origin + ', ' + requisition.name
            else:
                self.origin = requisition.name
        self.notes = requisition.description
        self.date_order = requisition.date_end or fields.Datetime.now()
        self.picking_type_id = requisition.picking_type_id.id

        if requisition.type_id.line_copy != 'copy':
            return

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context({
                'lang': partner.lang,
                'partner_id': partner.id,
            })
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            if fpos:
                taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(
                    lambda tax: tax.company_id == requisition.company_id)).ids
            else:
                taxes_ids = line.product_id.supplier_taxes_id.filtered(
                    lambda tax: tax.company_id == requisition.company_id).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0

            # Compute price_unit in appropriate currency
            if requisition.company_id.currency_id != currency:
                price_unit = requisition.company_id.currency_id.compute(price_unit, currency)

            # Create PO line
            order_line_values = line._prepare_purchase_order_line(
                name=name, product_qty=product_qty, price_unit=price_unit,
                taxes_ids=taxes_ids)
            order_line_values.update({"requisition_line_id": line.id,
                                      "account_analytic_id": line.account_analytic_id.id})

            order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines

    @api.constrains('incoterm_id', 'payment_term_id', 'fiscal_position_id')
    def quantity_done_with_product_uom_qty_constrains(self):
        if self.requisition_id.state in ['draft', 'in_progress']:
            if not self.env.user.has_group('purchase.group_purchase_user'):
                raise ValidationError(_('Sorry, you do not have permission to edit this field'))

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

    def action_view_invoice(self, invoices=False):
        total_amount = 0
        result = super(PurchaseOrder, self).action_view_invoice(invoices)
        for line in self.order_line:
            if line.product_id.purchase_method == 'purchase':
                qty = line.product_qty - line.qty_invoiced
            else:
                qty = line.qty_received - line.qty_invoiced
            total_amount += line.taxes_id and \
                            line.taxes_id.compute_all(line.price_unit, self.currency_id, qty)['total_included'] or \
                            line.price_unit * qty
        modules = self.env['ir.module.module'].sudo().search([('state', '=', 'installed'),
                                                              ('name', '=', 'contract')])
        if modules:
            result['context']['default_contract_id'] = self.contract_id.id
            result['context']['default_installment_amount'] = total_amount
            # result['context']['default_tax'] = taxes and [(6,0,taxes)]
            result['context']['create_installment'] = True
        return result

    def print_order_sample(self):
        # self.requisition_id.prepare_state_changing_user_list()
        return self.env.ref('purchase_custom_vro.custom_purchase_order_report').report_action(self)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    requisition_line_id = fields.Many2one("purchase.requisition.line")
