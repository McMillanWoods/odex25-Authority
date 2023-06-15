
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    
    _inherit = 'account.payment'
    
    def action_notify_payment(self, payment):
        # Send Notifications
        subject = _('Payment Notification') + ' - {}'.format(payment.partner_id.name)
        message = '{} '.format(payment.partner_id.name) + _('is successfully paid.') + '\n' + _('Payment Amount: ') + '{}'.format(payment.amount) + '\n' + _('Ref: ') + '{}'.format(payment.ref) + '\n' + _('On Date: ') + '{}'.format(payment.date)
        group = 'purchase.group_purchase_manager'
        # author_id = payment.create_uid.partner_id.id or None
        author_id = self.env.user.partner_id.id or None
        self.env.user.partner_id.send_notification_message(subject=subject, body=message, author_id=author_id, group=group)

    @api.model
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        # print("Hi payment!", res.amount)
        self.action_notify_payment(res)
        
        return res