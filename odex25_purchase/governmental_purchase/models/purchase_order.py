# -*- coding: utf-8 -*-
from odoo.exceptions import  ValidationError
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class PurchaseOrderCustom(models.Model):
    _inherit = "purchase.order"

    auto_notification = fields.Boolean()
    responsible_id = fields.Many2one('res.users')
    notify_before = fields.Integer()
    start_date = fields.Date()
    end_date = fields.Date()
    cron_end_date = fields.Date(compute="get_cron_end_date", store=True)
    contract_name = fields.Char(srting='Contract Name')
    period_type = fields.Selection(selection=[('day', 'Day(s)'), ('week', 'Week(s)'),
                                              ('month', 'Month(s)'), ('year', 'Year(s)')])
    type = fields.Selection(selection=[('ordinary', 'Ordinary'), ('contract', 'Contract')],
                            default='ordinary')
    billed_amount = fields.Float(store=True, compute='_compute_amount')
    remaining_amount = fields.Float(store=True, compute='_compute_amount')

    @api.depends('invoice_ids','invoice_count')
    def _compute_amount(self):
        for order in self:
            billed_amount = 0.0
            for invoice in order.invoice_ids:
                billed_amount += invoice.amount_total

            currency = order.currency_id or order.partner_id.property_purchase_currency_id or \
                self.env.company.currency_id
            order.update({
                'billed_amount': currency.round(billed_amount),
                'remaining_amount': order.amount_total - billed_amount,
            })

    @api.onchange('type')
    def auto_type_change(self):
        if self.type != 'contract':
            self.auto_notification = False
            self.responsible_id = False
            self.notify_before = 0
            self.start_date = None
            self.end_date = None
            self.contract_name = ''
            self.period_type = ''

            return {}

    @api.constrains('end_date', 'start_date', 'auto_notification')
    def start_notify_constrain(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.start_date >= rec.end_date:
                    raise ValidationError(_("Start Date Should Be Less Than End Date"))

                if rec.auto_notification and rec.notify_before < 1:
                    raise ValidationError(_("Notify Before End Should Be Greater Than Zero"))

    @api.depends('end_date', 'notify_before', 'period_type')
    def get_cron_end_date(self):
        for rec in self:
            if rec.end_date and rec.period_type:
                end = fields.Datetime.from_string(rec.end_date)
                date_to = False
                if rec.period_type == 'day':
                    date_to = (end + relativedelta(days=-rec.notify_before))
                elif rec.period_type == 'month':
                    date_to = (end + relativedelta(months=-rec.notify_before))
                elif rec.period_type == 'week':
                    date_to = (end + relativedelta(weeks=-rec.notify_before))
                elif rec.period_type == 'year':
                    date_to = (end + relativedelta(years=-rec.notify_before))
                rec.cron_end_date = date_to

    @api.model
    def cron_po_auto_notify(self):
        date = fields.Date.today()
        records = self.env['purchase.order'].sudo().search(
            [('state', 'not in', ['cancel', 'done']), ('cron_end_date', '<=', str(date)),
             ('auto_notification', '=', True)])
        for rec in records:
            template = self.env.ref('purchase_requisition_custom.auto_po_notify')
            template.send_mail(rec.id, force_send=True)

    def open_convert_po_contract(self):
        context = dict(self.env.context or {})
        context['default_purchase_id'] = self.id
        context['default_contract_name'] = self.contract_name
        context['default_responsible_id'] = self.responsible_id.id
        context['default_start_date'] = self.start_date
        context['default_end_date'] = self.end_date
        context['default_auto_notification'] = self.auto_notification
        context['purchase_id'] = self.id

        view = self.env.ref('governmental_purchase.convert_to_contract_po_wizard')
        wiz = self.env['convert.po.contract.wizard']
        return {
            'name': _('Purchase To Contract'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'convert.po.contract.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': context,
        }

    def action_recommend(self):
        for order in self:
            order.recommendation_order = True

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'sign']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True
