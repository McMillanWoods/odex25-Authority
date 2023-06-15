
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    
    _inherit = 'account.payment'
    

    def action_notify_payment(self, payment):
        message_users = []
        # for user in payment.message_follower_ids:
        #     if user not in message_users:
        #         message_users.append(user)

        if payment.invoice_user_id and payment.invoice_user_id not in message_users:
                message_users.append(payment.invoice_user_id)

        if payment.user_id and payment.user_id not in message_users:
                message_users.append(payment.user_id)

        # Send Notifications
        for user in message_users:
            subject = _('Payment Notification') + ' - {}'.format(payment.partner_id.name)
            message = '{} '.format(payment.partner_id.name) + _('is successfully paid.') + '\n' + _('Payment Amount: ') + '{}'.format(payment.amount) + '\n' + _('Ref: ') + '{}'.format(payment.ref) + '\n' + _('On Date: ') + '{}'.format(payment.date)
            group = 'purchase.group_purchase_manager'
            user.partner_id.send_notification_message(subject=subject, body=message, group=group)
            # print(message)

    @api.model
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        # print("Hi payment!", res.amount)
        self.action_notify_payment(res)
        
        return res