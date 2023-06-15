# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class ConvertPoContract(models.TransientModel):
  

    _name = "convert.po.contract.wizard"
    _description = "Convert Contract wizard"

    purchase_id = fields.Many2one('purchase.order')
    contract_name = fields.Char(srting='Contract Name')
    # New Added features on PO (related the cotract features)
    auto_notification = fields.Boolean()
    responsible_id = fields.Many2one('res.users')
    notify_before = fields.Integer()
    start_date = fields.Date()
    end_date = fields.Date()
    # cron_end_date = fields.Date(compute="get_cron_end_date",store=True)
    period_type = fields.Selection(selection=[('day','Day(s)'),('week','Week(s)'),('month','Month(s)'),('year','Year(s)')])

    @api.onchange('auto_notification')
    def auto_notification_onchange(self):
        if self.auto_notification is False:
            self.notify_before = 0
            self.period_type = ''

            return {}

    @api.constrains('end_date','start_date', 'auto_notification')
    def start_notify_constrain(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.start_date >= rec.end_date:
                    raise ValidationError(_("Start Date Should Be Less Than End Date"))

                if rec.auto_notification and rec.notify_before <1:
                    raise ValidationError(_("Notify Before End Should Be Greater Than Zero"))

    # @api.depends('end_date','notify_before','period_type')
    # def get_cron_end_date(self):
    #     for rec in self:
    #         if rec.end_date and rec.period_type:
    #             end = fields.Datetime.from_string(rec.end_date)
    #             type = self.period_type
    #             date_to = False
    #             if rec.period_type == 'day':
    #                 date_to = (end + relativedelta(days=-rec.notify_before))
    #             elif rec.period_type == 'month':
    #                 date_to = (end + relativedelta(months=-rec.notify_before))
    #             elif rec.period_type == 'week':
    #                 date_to = (end + relativedelta(weeks=-rec.notify_before))
    #             elif rec.period_type == 'year':
    #                 date_to = (end + relativedelta(years=-rec.notify_before))
    #             rec.cron_end_date = date_to

    @api.model
    def default_get(self, fields):
        res = super(ConvertPoContract, self).default_get(fields)
        purchase_id = self.env.context.get('purchase_id', False)
      
        res.update({
            'purchase_id': purchase_id if purchase_id else False,
        })
        return res

    def action_create_contract(self):
        self.ensure_one()
        self.purchase_id.write({
            'type':'contract',
            'contract_name':self.contract_name,

            'auto_notification':self.auto_notification,
            'responsible_id':self.responsible_id.id,
            'notify_before':self.notify_before,
            'start_date':self.start_date,
            'end_date':self.end_date,
            'period_type':self.period_type
        })


        return {'type': 'ir.actions.act_window_close'}
    