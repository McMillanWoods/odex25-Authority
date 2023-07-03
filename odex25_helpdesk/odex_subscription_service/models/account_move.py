# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta

class AccountMove(models.Model):
    _inherit = 'account.move'

    subscription_id = fields.Many2one('subscription.service', string="Subscription")

    def button_cancel(self):
        # action_invoice_cancel
        for inv in self.filtered(lambda i: i.subscription_id and i.payment_state == 'not_paid'):
            sub = inv.subscription_id
            sub.recurring_next_date -= relativedelta(months=1)
            paid_inv_count = len(sub.invoice_ids.filtered(lambda i: i.payment_state == 'paid'))
            current_date = sub.date_start + relativedelta(months=paid_inv_count)
            if sub.recurring_next_date < current_date:
                sub.recurring_next_date = current_date
            body = '{} '.format(inv.name) + _('has been cancelled on subscription') + ' {}.'.format(sub.display_name) + _('A new invoice will be issued.') 
            sub.message_post(body=body, message_type='comment',**{'subtype_id': 1})
        return super(AccountMove,self).button_cancel()

