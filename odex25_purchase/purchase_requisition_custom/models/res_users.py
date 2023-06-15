
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def send_notification_message(self, subject, body, group=None):
        """Send notification"""
        if group:
            partner_ids = self.env.ref(group).users.mapped('partner_id').ids
            # partner_ids = self.env['res.partner'].search([('id', 'in', users)]).mapped('id')
        else:
            partner_ids = [self.id]

        if partner_ids:
            try:
                self.message_post(type="notification", subject=subject, body=body, author_id=None,
                     partner_ids=partner_ids,
                     subtype_xmlid="mail.mt_comment")
            except Exception as e:
                pass
            