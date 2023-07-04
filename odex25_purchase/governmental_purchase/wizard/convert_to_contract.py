# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ConvertPoContract(models.TransientModel):
    _name = "convert.po.contract.wizard"
    _description = "Convert Contract wizard"

    purchase_id = fields.Many2one('purchase.order')
    contract_name = fields.Char()
    auto_notification = fields.Boolean()
    responsible_id = fields.Many2one('res.users')
    notify_before = fields.Integer()
    start_date = fields.Date()
    end_date = fields.Date()
    period_type = fields.Selection(
        selection=[('day', 'Day(s)'), ('week', 'Week(s)'), ('month', 'Month(s)'), ('year', 'Year(s)')])

    @api.onchange('auto_notification')
    def auto_notification_onchange(self):
        if not self.auto_notification:
            self.notify_before = 0
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

    def action_create_contract(self):
        self.ensure_one()
        self.purchase_id.write({
            'type': 'contract',
            'contract_name': self.contract_name,
            'auto_notification': self.auto_notification,
            'responsible_id': self.responsible_id.id,
            'notify_before': self.notify_before,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'period_type': self.period_type
        })
        return {'type': 'ir.actions.act_window_close'}
